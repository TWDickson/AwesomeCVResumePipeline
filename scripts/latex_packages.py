#!/usr/bin/env python3
"""
Dynamic LaTeX Package Manager for Tectonic

Automatically detects all LaTeX package dependencies in the project,
checks if Tectonic has them, and downloads missing packages from CTAN.

Usage:
    python scripts/latex_packages.py --check     # Check for missing packages
    python scripts/latex_packages.py --install   # Install missing packages
    python scripts/latex_packages.py --scan      # Show all detected dependencies
    python scripts/latex_packages.py --clean     # Remove downloaded packages
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError
from typing import Set, Dict, Optional, List


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def print_status(message, status='info'):
    """Print colored status messages"""
    if status == 'success':
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    elif status == 'error':
        print(f"{Colors.RED}✗{Colors.RESET} {message}")
    elif status == 'warning':
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")
    elif status == 'info':
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")


class DependencyScanner:
    """Scans LaTeX files for package dependencies"""

    # Packages that are built into LaTeX or Tectonic, no need to download
    BUILTIN_PACKAGES = {
        'article', 'book', 'report', 'letter', 'minimal',  # Document classes
        'amsmath', 'amssymb', 'amsfonts', 'amsthm',  # AMS packages (usually included)
        'graphicx', 'color', 'xcolor', 'geometry', 'fancyhdr',  # Common packages
        'inputenc', 'fontenc', 'babel',  # Encoding packages (not needed for XeTeX)
        'hyperref', 'url', 'natbib', 'cite',  # Common citation/link packages
    }

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def find_tex_files(self) -> List[Path]:
        """Find all .tex and .cls files in the project"""
        tex_files = []

        # Find .tex files (excluding build directories)
        for pattern in ['*.tex', '*.cls', '**/*.tex', '**/*.cls']:
            for file in self.project_root.glob(pattern):
                # Skip build/output directories
                if any(p in file.parts for p in ['build', '_output', 'texmf', '.git']):
                    continue
                tex_files.append(file)

        return tex_files

    def extract_packages_from_file(self, file_path: Path) -> Set[str]:
        """Extract package names from a single LaTeX file"""
        packages = set()

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Match \usepackage and \RequirePackage commands
            # Handles: \usepackage{pkg}, \usepackage[options]{pkg}, \RequirePackage{pkg}
            patterns = [
                r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}',
                r'\\RequirePackage(?:\[[^\]]*\])?\{([^}]+)\}',
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Handle comma-separated packages: \usepackage{pkg1,pkg2,pkg3}
                    package_list = match.group(1)
                    for pkg in package_list.split(','):
                        pkg = pkg.strip()
                        if pkg and pkg not in self.BUILTIN_PACKAGES:
                            packages.add(pkg)

        except Exception as e:
            print_status(f"Warning: Could not read {file_path}: {e}", 'warning')

        return packages

    def scan_all_dependencies(self) -> Dict[str, Set[Path]]:
        """Scan all LaTeX files and return dependencies with their sources"""
        dependencies = {}  # package_name -> set of files that use it

        tex_files = self.find_tex_files()
        print_status(f"Scanning {len(tex_files)} LaTeX files...", 'info')

        for tex_file in tex_files:
            packages = self.extract_packages_from_file(tex_file)
            for pkg in packages:
                if pkg not in dependencies:
                    dependencies[pkg] = set()
                dependencies[pkg].add(tex_file)

        return dependencies


class TectonicChecker:
    """Checks if packages are available in Tectonic"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.cache_file = project_root / '.tectonic_package_cache.json'
        self.cache = self.load_cache()

    def load_cache(self) -> dict:
        """Load cached package availability results"""
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except json.JSONDecodeError:
                return {}
        return {}

    def save_cache(self):
        """Save package availability cache"""
        self.cache_file.write_text(json.dumps(self.cache, indent=2))

    def test_package_availability(self, package_name: str) -> bool:
        """Test if Tectonic can find a package by trying to compile a minimal document"""

        # Check cache first
        if package_name in self.cache:
            return self.cache[package_name]

        # Create minimal test document
        test_doc = f"""\\documentclass{{article}}
\\usepackage{{{package_name}}}
\\begin{{document}}
Test
\\end{{document}}
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / 'test.tex'
            test_file.write_text(test_doc)

            try:
                # Try to compile with Tectonic
                result = subprocess.run(
                    ['tectonic', '--chatter', 'minimal', str(test_file)],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Package is available if compilation succeeded
                available = result.returncode == 0

                # Cache the result
                self.cache[package_name] = available
                self.save_cache()

                return available

            except subprocess.TimeoutExpired:
                print_status(f"Timeout testing {package_name}", 'warning')
                return False
            except Exception as e:
                print_status(f"Error testing {package_name}: {e}", 'warning')
                return False


class CTANDownloader:
    """Downloads packages from CTAN"""

    CTAN_MIRRORS = [
        'https://mirrors.ctan.org',
        'https://ctan.org',
    ]

    def __init__(self, texmf_dir: Path):
        self.texmf_dir = texmf_dir
        self.cache_dir = texmf_dir / '.cache'
        self.metadata_file = self.cache_dir / 'installed_packages.json'

    def ensure_directories(self):
        """Create necessary directories"""
        self.texmf_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)

    def load_metadata(self) -> dict:
        """Load installed package metadata"""
        if self.metadata_file.exists():
            try:
                return json.loads(self.metadata_file.read_text())
            except json.JSONDecodeError:
                return {}
        return {}

    def save_metadata(self, metadata: dict):
        """Save installed package metadata"""
        self.metadata_file.write_text(json.dumps(metadata, indent=2))

    def is_package_installed(self, package_name: str) -> bool:
        """Check if package is already downloaded and installed"""
        metadata = self.load_metadata()
        return package_name in metadata and metadata[package_name].get('installed', False)

    def download_file(self, url: str, description: str = "file") -> Optional[bytes]:
        """Download a file from URL"""
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=30) as response:
                return response.read()
        except URLError as e:
            return None

    def try_download_from_ctan(self, package_name: str) -> Optional[bytes]:
        """Try to download package from CTAN mirrors"""

        # Try different CTAN paths
        possible_paths = [
            f'/tex-archive/macros/latex/contrib/{package_name}.tar.gz',
            f'/tex-archive/macros/latex/contrib/{package_name}.zip',
            f'/tex-archive/fonts/{package_name}.tar.gz',
            f'/tex-archive/fonts/{package_name}.zip',
            f'/tex-archive/macros/latex/required/{package_name}.tar.gz',
        ]

        for mirror in self.CTAN_MIRRORS:
            for path in possible_paths:
                url = mirror + path
                print(f"  {Colors.DIM}Trying {url}{Colors.RESET}")

                content = self.download_file(url, package_name)
                if content:
                    return content

        return None

    def extract_archive(self, content: bytes, package_name: str) -> bool:
        """Extract package archive to texmf directory"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_path = temp_path / 'package.archive'
            archive_path.write_bytes(content)

            # Try to extract as tar.gz
            try:
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(temp_path)
            except:
                # Try as zip
                try:
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_path)
                except Exception as e:
                    print_status(f"Failed to extract archive: {e}", 'error')
                    return False

            # Find and copy relevant files
            files_copied = 0

            # Look for .sty, .cls, .def, .fd, .otf, .ttf files
            for ext in ['*.sty', '*.cls', '*.def', '*.fd', '*.otf', '*.ttf', '*.pfb']:
                for file_path in temp_path.rglob(ext):
                    # Copy to texmf root (flatten structure for simplicity)
                    dest = self.texmf_dir / file_path.name
                    shutil.copy2(file_path, dest)
                    files_copied += 1

            return files_copied > 0

    def install_package(self, package_name: str) -> bool:
        """Download and install a package from CTAN"""

        if self.is_package_installed(package_name):
            return True

        print(f"\n{Colors.BOLD}Downloading {package_name} from CTAN...{Colors.RESET}")

        content = self.try_download_from_ctan(package_name)
        if not content:
            print_status(f"Could not download {package_name} from CTAN", 'error')
            return False

        print_status(f"Downloaded {len(content) // 1024}KB", 'success')

        # Extract and install
        if self.extract_archive(content, package_name):
            # Update metadata
            metadata = self.load_metadata()
            metadata[package_name] = {
                'installed': True,
                'source': 'CTAN'
            }
            self.save_metadata(metadata)

            print_status(f"{package_name} installed successfully", 'success')
            return True
        else:
            print_status(f"Failed to install {package_name}", 'error')
            return False


class PackageManager:
    """Main package manager coordinating all components"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.texmf_dir = self.project_root / 'texmf'

        self.scanner = DependencyScanner(self.project_root)
        self.tectonic_checker = TectonicChecker(self.project_root)
        self.downloader = CTANDownloader(self.texmf_dir)

    def scan_dependencies(self) -> Dict[str, Set[Path]]:
        """Scan and display all package dependencies"""
        print(f"\n{Colors.BOLD}Scanning LaTeX Dependencies{Colors.RESET}")

        dependencies = self.scanner.scan_all_dependencies()

        if not dependencies:
            print_status("No package dependencies found", 'info')
            return {}

        print(f"\n{Colors.BOLD}Found {len(dependencies)} packages:{Colors.RESET}")
        for pkg in sorted(dependencies.keys()):
            files = dependencies[pkg]
            print(f"  {Colors.CYAN}{pkg:30}{Colors.RESET} used in {len(files)} file(s)")

        return dependencies

    def check_packages(self, auto_fix: bool = False) -> bool:
        """Check all dependencies and identify missing packages"""
        print(f"\n{Colors.BOLD}Checking Package Availability{Colors.RESET}")

        dependencies = self.scanner.scan_all_dependencies()
        if not dependencies:
            print_status("No package dependencies to check", 'info')
            return True

        missing_packages = []
        available_packages = []

        for pkg in sorted(dependencies.keys()):
            # Skip if already downloaded locally
            if self.downloader.is_package_installed(pkg):
                print(f"  {Colors.CYAN}{pkg:30}{Colors.RESET} ", end='')
                print_status("Local", 'success')
                available_packages.append(pkg)
                continue

            # Test with Tectonic
            print(f"  {Colors.CYAN}{pkg:30}{Colors.RESET} ", end='')
            sys.stdout.flush()

            if self.tectonic_checker.test_package_availability(pkg):
                print_status("Tectonic", 'success')
                available_packages.append(pkg)
            else:
                print_status("Missing", 'warning')
                missing_packages.append(pkg)

        # Summary
        print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
        print(f"  Available:  {len(available_packages)}")
        print(f"  Missing:    {len(missing_packages)}")

        if missing_packages:
            print(f"\n{Colors.YELLOW}Missing packages:{Colors.RESET}")
            for pkg in missing_packages:
                print(f"  - {pkg}")

            if auto_fix:
                print(f"\n{Colors.BOLD}Auto-installing missing packages...{Colors.RESET}")
                return self.install_missing_packages(missing_packages)
            else:
                print(f"\n{Colors.YELLOW}Run with --install to download missing packages{Colors.RESET}")
                return False

        print_status("\nAll required packages are available!", 'success')
        return True

    def install_missing_packages(self, packages: List[str]) -> bool:
        """Install a list of missing packages"""
        self.downloader.ensure_directories()

        success_count = 0
        for pkg in packages:
            if self.downloader.install_package(pkg):
                success_count += 1

        print(f"\n{Colors.BOLD}Installation Summary:{Colors.RESET}")
        print(f"  Installed: {success_count}/{len(packages)}")

        return success_count == len(packages)

    def install_all_missing(self) -> bool:
        """Check and install all missing packages"""
        return self.check_packages(auto_fix=True)

    def clean(self):
        """Remove all downloaded packages"""
        if not self.texmf_dir.exists():
            print_status("No packages to clean", 'info')
            return

        print(f"\n{Colors.BOLD}Cleaning downloaded packages...{Colors.RESET}")
        print(f"  Removing: {self.texmf_dir}")

        try:
            shutil.rmtree(self.texmf_dir)
            print_status("Packages removed", 'success')
        except Exception as e:
            print_status(f"Error cleaning packages: {e}", 'error')


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Dynamic LaTeX Package Manager for Tectonic',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/latex_packages.py --scan      # Show all dependencies
  python scripts/latex_packages.py --check     # Check package availability
  python scripts/latex_packages.py --install   # Download missing packages
  python scripts/latex_packages.py --clean     # Remove downloaded packages
        """
    )
    parser.add_argument('--scan', action='store_true',
                       help='Scan and display all package dependencies')
    parser.add_argument('--check', action='store_true',
                       help='Check package availability in Tectonic')
    parser.add_argument('--install', action='store_true',
                       help='Install missing packages from CTAN')
    parser.add_argument('--clean', action='store_true',
                       help='Remove downloaded packages')
    parser.add_argument('--project-root', type=str,
                       help='Project root directory (default: current directory)')

    args = parser.parse_args()

    # If no arguments, show help
    if not any([args.scan, args.check, args.install, args.clean]):
        parser.print_help()
        return 0

    manager = PackageManager(args.project_root)

    if args.clean:
        manager.clean()
    elif args.scan:
        manager.scan_dependencies()
    elif args.install:
        success = manager.install_all_missing()
        return 0 if success else 1
    elif args.check:
        success = manager.check_packages(auto_fix=False)
        return 0 if success else 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
