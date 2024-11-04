
# Machine Staging Application

This application provides a graphical interface for staging machines and transferring files between them using Firebase for real-time data handling. Built with `customtkinter` for a dark-themed UI, it allows file uploads, machine selection, and Firebase-integrated machine states.

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Firebase Setup](#firebase-setup)
4. [Running the Application](#running-the-application)
5. [Usage Guide](#usage-guide)

## Features

- **Machine Selection**: Choose machines for staging with check/uncheck all options.
- **File Upload**: Upload and assign envelope or letter files to selected machines.
- **File Transfer**: Transfer files to specified directories with real-time progress indicators.
- **Firebase Integration**: Real-time updates and state synchronization with Firebase.
- **Error Handling**: Clear error handling and logging for transfer failures.
- **Logging**: Logs actions and errors to `app_debug.log`.

## Installation

### Prerequisites
- Python 3.7 or higher
- Firebase Realtime Database

### Dependencies
Install required libraries using `pip`:
```bash
pip install customtkinter pillow dotenv pyrebase4
```

### Environment Configuration

Store sensitive Firebase configuration in a `.env` file for security. Create a `.env` file in the root directory with the following:

```plaintext
API_KEY=your_api_key
AUTH_DOMAIN=your_auth_domain
DATABASE_URL=your_database_url
STORAGE_BUCKET=your_storage_bucket
```

### Firebase Setup

1. **Initialize Firebase in your project** and enable the Realtime Database.
2. **Structure of Firebase Data**:
   - Set up a `machine_states` node with keys for each machine’s state.
   - Use the `initialize_machine_states_in_firebase()` function to initialize machine states.

## Running the Application

1. Run the application:
   ```bash
   python app.py
   ```

2. Logs will be saved to `app_debug.log` for troubleshooting.

## Usage Guide

### Interface Overview

- **Frame 1** - Machine Selection: Allows selecting machines for staging.
  - Use check/uncheck all buttons to select or deselect all machines.
  - `IN-USE` and `AVAILABLE` checkboxes provide visual indicators of machine states.

- **Frame 2** - File Uploads: Upload envelope or letter files for assignment to machines.
  - Select files for upload and review selected files in the scrollable area.
  - Submit to proceed to file assignment.

- **Frame 3** - File Transfer and Status: View file assignments and monitor transfer status.
  - Progress bars show real-time file transfer progress.
  - Failed transfers are indicated in red; completed transfers in green.

### Functions

- **File Transfer**: Transfer files to designated machine directories, with progress tracking and error handling.
- **Delete .bin Files**: Deletes `.bin` files from selected machine directories before transfer.
- **Stream Updates**: Firebase provides real-time updates to machine states.

### Troubleshooting

- Ensure `.env` is in the correct directory.
- Check `app_debug.log` for error logs.
- Ensure Firebase credentials are valid.
