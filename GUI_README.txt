Scene Manager GUI
=================

This repository also includes a small desktop GUI called Scene Manager, built with Tkinter and Pillow.
The application provides a simple visual layer around an image-based scanning workflow: it shows the latest scan,
keeps a short visual history, lists previously created image files, and makes it easy to save copies of selected results.

The GUI is intentionally straightforward. It is not meant to be a large scanning suite or a general-purpose image
management application. Instead, it focuses on one practical use case: monitoring a scan output folder, previewing the
newest results, and giving quick access to recent scan history in a compact desktop interface.

This is the final version for my own needs. I do not plan to continue developing it further. It solves the problem I
built it for, and that is enough for me. If somebody has a similar use case, they are welcome to clone the project and
modify it however they like.


What the GUI does
-----------------

At startup, the GUI opens a desktop window titled "Scene Manager" and works with a configurable image directory. The
application continuously monitors that folder and refreshes its content automatically at a fixed interval.

The GUI supports common image formats, including JPG, JPEG, PNG, BMP, TIF, TIFF, and WEBP. Files in the selected image
folder are scanned, filtered by extension, and sorted by modification time so that the newest images appear first.


Interface overview
------------------

The interface is divided into three main areas:

1. Recent thumbnail strip

At the top of the window, the GUI displays a strip of the four most recent image thumbnails. This gives a quick visual
summary of the latest scan results without needing to open files manually. If fewer than four images are available,
the remaining slots show a placeholder message instead.

2. Main preview and folder information

On the left side of the main area, the GUI shows a larger preview of the most recent scan. This preview displays the
newest image in the monitored folder, scaled to fit the preview area while preserving aspect ratio. If a file cannot be
opened as an image, the GUI reports that the image is unreadable instead of crashing.

Below the preview, the GUI shows a small information panel with basic folder statistics:
- the current folder path,
- the number of detected image files,
- the total size of the folder contents,
- drive usage information for the storage location,
- and the timestamp of the last refresh cycle.

The GUI also includes a folder picker button so the monitored image directory can be changed interactively at runtime.

3. File history list

On the right side, the GUI displays a file list showing:
- file name,
- file size,
- and modification date/time.

This list acts as a simple scan history view. Selecting an entry updates the main preview, allowing the user to browse
older results visually without leaving the application.


Buttons
-------

The bottom row contains three buttons: SCAN, CONNECT, and SAVE.

SCAN
The SCAN button is currently present as a placeholder. It opens an informational dialog and marks the place where an
actual scan command or backend could be integrated if needed.

CONNECT
The CONNECT button is also implemented as a placeholder. It opens an informational dialog and represents the location
where scanner setup or backend configuration could be attached.

SAVE
The SAVE button is fully functional. It allows the user to save a copy of the currently selected image. If no file is
selected in the history list, the GUI automatically falls back to the newest available image. The file is then copied
to a user-chosen destination through a standard "Save As" dialog.


How updates are handled
-----------------------

The GUI does not rely on a complex indexing system or background database. Instead, it uses a lightweight refresh
approach: it repeatedly scans the current image folder, builds a small snapshot from the most recent files, and updates
the interface only when a change is detected. This keeps the application simple while still making it responsive enough
for a practical scan-monitoring workflow.

Image thumbnails and the main preview are generated dynamically using Pillow. Both thumbnail generation and preview
rendering preserve aspect ratio and place the image onto a neutral background so that files of different dimensions
remain easy to view in a consistent layout.


Scope and philosophy
--------------------

This GUI was built to solve a specific, personal workflow problem. It is intentionally narrow in scope and intentionally
simple in structure. It is not trying to compete with full scanner software, asset managers, or archival tools.

Because of that, I consider this version complete. The project already does what I need:
- it monitors a scan output folder,
- it shows the newest result immediately,
- it keeps a visible short history through thumbnails and a file list,
- and it allows selected results to be saved elsewhere.

I do not plan to extend it beyond this. If you clone the repository and the GUI fits your own workflow, feel free to
keep it as-is or adapt it however you want.


Requirements
------------

The GUI is written in Python 3 and uses:
- Tkinter for the desktop interface,
- Pillow for image loading, scaling, thumbnail generation, and preview rendering.

If Pillow is not installed, the application exits with an error message.


Summary
-------

The Scene Manager GUI is a small, purpose-built desktop utility for watching a folder of scanned images, previewing the
latest result, browsing recent history, and copying selected files to another location. It is simple by design,
finished for its original purpose, and open to reuse by anyone who finds the same workflow useful.
