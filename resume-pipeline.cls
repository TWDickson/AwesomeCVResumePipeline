%% Start of file `resume-pipeline.cls'.
% Resume Pipeline Class File
%
% This class extends Awesome-CV with custom automation features
% and personalized styling for the resume generation pipeline.
%
% Based on: Awesome-CV by Claud D. Park
% https://github.com/posquit0/Awesome-CV
%
% Author: Your Name
% Created: 2025/10/21
%
% Class license:
% LPPL v1.3c (http://www.latex-project.org/lppl)
%


%-------------------------------------------------------------------------------
%                Identification
%-------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{resume-pipeline}[2025/10/21 v1.0.0 Resume Pipeline Class]


%-------------------------------------------------------------------------------
%                Load Base Class
%-------------------------------------------------------------------------------
% Load the Awesome-CV class from the AwesomeCV subdirectory
\LoadClass{AwesomeCV/awesome-cv}


%-------------------------------------------------------------------------------
%                Required Packages for Custom Features
%-------------------------------------------------------------------------------
\RequirePackage{expl3}		% For LaTeX3 syntax (section loading)
\RequirePackage{shellesc}	% For shell escape file operations
\RequirePackage{xpatch}		% For surgical patching of commands


%-------------------------------------------------------------------------------
%                Custom Spacing Overrides
%-------------------------------------------------------------------------------
% Tighter section spacing for more compact layout
\renewcommand{\acvSectionTopSkip}{0mm}				% was 3mm in original
\renewcommand{\acvSectionContentTopSkip}{2mm}		% keep as is


%-------------------------------------------------------------------------------
%                Custom Mobile Commands
%-------------------------------------------------------------------------------

% New command: \mobilelabel - Display custom label instead of number
% Usage: \mobilelabel{<mobile number>}{<display label>}
% Example: \mobilelabel{5551234567}{Mobile} or \mobilelabel{+15551234567}{+1 (555) 123-4567}
\newcommand*{\mobilelabel}[2]{%
	\def\@mobile{#1}%
	\def\@mobilelabel{#2}%
	\def\@usemobilelabel{true}%
}

%-------------------------------------------------------------------------------
%                Custom Header Styling Patches
%-------------------------------------------------------------------------------
% Patch 1: Change last name from bold to light font weight
\xpatchcmd{\makecvheader}
	{\headerlastnamestyle}
	{\headerfirstnamestyle}
	{}{\ClassWarning{resume-pipeline}{Failed to patch header name style}}

% Patch 2: Smart mobile display - use label if \mobilelabel was used, otherwise use number
\xpatchcmd{\makecvheader}
	{\href{\@teluri}{\faMobile\acvHeaderIconSep\@mobile}}
	{\ifdefined\@usemobilelabel%
		\href{tel:\@mobile}{\faMobile\acvHeaderIconSep\@mobilelabel}%
	\else%
		\href{\@teluri}{\faMobile\acvHeaderIconSep\@mobile}%
	\fi}
	{}{\ClassWarning{resume-pipeline}{Failed to patch mobile display logic}}


%-------------------------------------------------------------------------------
%                Custom Entry Environment Patches
%-------------------------------------------------------------------------------
% Patch cventries: Adjust spacing
\xpatchcmd{\cventries}
	{\vspace{\acvSectionContentTopSkip}}
	{\vspace{-8pt}}
	{}{\ClassWarning{resume-pipeline}{Failed to patch cventries spacing}}

% Patch cventry: Change negative spacing to positive
\xpatchcmd{\cventry}
	{\vspace{-2.0mm}}
	{\vspace{2.0mm}}
	{}{\ClassWarning{resume-pipeline}{Failed to patch cventry vspace}}

% Patch cventry: Increase tabcolsep from 0pt to 5pt
\xpatchcmd{\cventry}
	{\setlength\tabcolsep{0pt}}
	{\setlength\tabcolsep{5pt}}
	{}{\ClassWarning{resume-pipeline}{Failed to patch cventry tabcolsep}}

% Patch cventry: Swap parameter order (title and position)
% Original: #2 is title, #1 is position
% Custom: #1 is title, #2 is position
\xpatchcmd{\cventry}
	{\entrytitlestyle{#2} & \entrylocationstyle{#3} \\
	 \entrypositionstyle{#1} & \entrydatestyle{#4} \\}
	{\entrytitlestyle{#1} & \entrylocationstyle{#3} \\
	 \entrypositionstyle{#2} & \entrydatestyle{#4}}
	{}{\ClassWarning{resume-pipeline}{Failed to patch cventry parameter order}}

% Patch cventry: Change ifstrempty to ifempty for consistency
\xpatchcmd{\cventry}
	{\ifstrempty{#5}}
	{\ifempty{#5}}
	{}{\ClassWarning{resume-pipeline}{Failed to patch cventry ifempty}}

% Patch cventry: Fix closing condition (remove extra \\)
\xpatchcmd{\cventry}
	{\entrypositionstyle{#1} & \entrydatestyle{#4} \\}
	{\entrypositionstyle{#1} & \entrydatestyle{#4}}
	{}{}  % Silent fail OK - depends on original version

% Patch cvskills: Change table width calculation
\xpatchcmd{\cvskills}
	{L{\textwidth * \real{0.9}}}
	{L{\textwidth - 5cm}}
	{}{\ClassWarning{resume-pipeline}{Failed to patch cvskills width}}

% Patch cvitems: Adjust parskip from 0pt to 1pt
\xpatchcmd{\cvitems}
	{\setlength{\parskip}{0pt}}
	{\setlength{\parskip}{1pt}}
	{}{\ClassWarning{resume-pipeline}{Failed to patch cvitems parskip}}

% Patch cvitems: Change closing vspace
\xpatchcmd{\cvitems}
	{\vspace{1.0mm}}
	{\vspace{-4.0mm}}
	{}{\ClassWarning{resume-pipeline}{Failed to patch cvitems closing vspace}}

% Patch cvitems: Add raggedright (append to opening)
\xapptocmd{\cvitems}
	{\raggedright}
	{}{\ClassWarning{resume-pipeline}{Failed to add raggedright to cvitems}}


%-------------------------------------------------------------------------------
%                Custom Commands - Compact Entry
%-------------------------------------------------------------------------------
% Define a compact entry for brief experience without description
% Usage: \cvcompactentry{<position>}{<title>}{<location>}{<date>}
\newcommand*{\cvcompactentry}[4]{%
	\vspace{2.0mm}
	\setlength\tabcolsep{5pt}
	\setlength{\extrarowheight}{-2pt}
	\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}} L{\textwidth - 4.5cm} R{4.5cm}}
		\ifempty{#2#3}%
			{\entrypositionstyle{#1} & \entrydatestyle{#4} \\}%
			{\entrytitlestyle{#1} & \entrylocationstyle{#3} \\[-1mm]
			 \entrypositionstyle{#2} & \entrydatestyle{#4} \\}%
	\end{tabular*}%
	\vspace{-1mm}
	\raggedright\noindent{\color{awesome}\rule{3cm}{3pt}}
}


%-------------------------------------------------------------------------------
%                Custom Commands - Dynamic Section Loading
%-------------------------------------------------------------------------------
% Define section loading system for dynamic content management
% This allows loading versioned content with fallback to defaults
\ExplSyntaxOn%
\cs_new_protected:Nn \resume_load_sections:n {
	\clist_map_inline:nn {#1} {
		\IfFileExists{Content/\OutputVersion/##1.tex}{
			\input{Content/\OutputVersion/##1.tex}
		}{
			\input{Content/default/##1.tex}
		}
	}
}
\cs_generate_variant:Nn \resume_load_sections:n { V }
\NewDocumentCommand{\loadSections}{m}{
	\resume_load_sections:n {#1}
}
\ExplSyntaxOff%


%-------------------------------------------------------------------------------
%                Custom Commands - Cover Letter Management
%-------------------------------------------------------------------------------
% Storage for cover letter content
\newcommand{\storedcoverletterinfo}{}
\newcommand{\storedcoverlettercontent}{}

% Custom commands to store cover letter content
\newcommand{\storerecipient}[2]{\recipient{#1}{#2}}
\newcommand{\storeletterdate}[1]{\letterdate{#1}}
\newcommand{\storelettertitle}[1]{\lettertitle{#1}}
\newcommand{\storeletteropening}[1]{\letteropening{#1}}
\newcommand{\storeletterclosing}[1]{\letterclosing{#1}}
\newcommand{\storeletterenclosure}[2][]{\letterenclosure[#1]{#2}}

% Custom environment to store cvletter content
\newenvironment{storedcvletter}
	{\global\let\storedcoverlettercontent\empty
	 \long\gdef\storedcoverlettercontent}
	{}

% Command to execute stored content
\newcommand{\executestoredcontent}{\storedcoverlettercontent}

% Main load command for cover letters
\newcommand{\loadCoverLetter}{%
	\IfFileExists{Content/\OutputVersion/cover_letter.tex}{
		\input{Content/\OutputVersion/cover_letter.tex}
	}{
		\input{Content/default/cover_letter.tex}
	}
}


%-------------------------------------------------------------------------------
%                Custom Commands - Build Automation
%-------------------------------------------------------------------------------
% Cross-platform file copy and markdown generation commands
% These enable automated PDF output and conversion in the build pipeline

% Generic file copy utility
\newcommand{\safefilecopy}[2]{%
	\newif\ifwindows%
	\IfFileExists{C:/Windows/System32/cmd.exe}{\windowstrue}{\windowsfalse}%
	\ifwindows%
		\ShellEscape{powershell -Command "Start-Sleep -Milliseconds 100; Copy-Item -Path '\string\jobname.pdf' -Destination 'Upload\space Copies\string\\\string\OutputVersion\string\\Your\space Name\space Resume.pdf' -Force"}%
	\else%
		\ShellEscape{mkdir -p "\detokenize{#2}" && sleep 0.1 && FILE=\string$(echo \detokenize{#1} | sed 's/"\string\string//g').pdf && cp "\string$FILE" "\detokenize{#2}/\string$FILE"}%
	\fi%
}

% Copy resume PDF and generate markdown
\newcommand{\saferesumecopy}[2]{%
	\newif\ifwindows%
	\IfFileExists{C:/Windows/System32/cmd.exe}{\windowstrue}{\windowsfalse}%
	\ifwindows%
		\ShellEscape{powershell -Command "Start-Sleep -Milliseconds 100; Copy-Item -Path '\string\jobname.pdf' -Destination 'Upload\space Copies\string\\\string\OutputVersion\string\\Your\space Name\space Resume.pdf' -Force; python latex\string_to\string_markdown.py"}%
	\else%
		\ShellEscape{mkdir -p "\detokenize{#2}" && sleep 0.1 && FILE=\string$(echo \detokenize{#1} | sed 's/"\string\string//g').pdf && cp "\string$FILE" "\detokenize{#2}/\string$FILE" && python3 latex\string_to\string_markdown.py}%
	\fi%
}

% Copy cover letter PDF and generate markdown
\newcommand{\safecoverlettercopy}[2]{%
	\newif\ifwindows%
	\IfFileExists{C:/Windows/System32/cmd.exe}{\windowstrue}{\windowsfalse}%
	\ifwindows%
		\ShellEscape{powershell -Command "Start-Sleep -Milliseconds 100; Copy-Item -Path '\string\jobname.pdf' -Destination 'Upload\space Copies\string\\\string\OutputVersion\string\\Your\space Name\space Cover\space Letter.pdf' -Force; python cover\string_letter\string_to\string_markdown.py"}%
	\else%
		\ShellEscape{mkdir -p "\detokenize{#2}" && sleep 0.1 && FILE=\string$(echo \detokenize{#1} | sed 's/"\string\string//g').pdf && cp "\string$FILE" "\detokenize{#2}/\string$FILE" && python3 cover\string_letter\string_to\string_markdown.py}%
	\fi%
}

%% End of file `resume-pipeline.cls'.
