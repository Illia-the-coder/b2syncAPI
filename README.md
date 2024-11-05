
# B2 Command Line Tool

Sync files to Backblaze B2 with filtering and multithreading.

## Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/Illia-the-coder/b2syncAPI.git
    cd b2syncAPI
    ```

2. **Install Dependencies**
    ```bash
    pip3 install -r requirements.txt
    ```

## Configuration

Set your B2 credentials:
```bash
export B2_KEY_ID='your_b2_key_id'
export B2_APP_KEY='your_b2_app_key'
```

## Usage

Run the synchronization script:
```bash
python3 src/sync_b2.py /path/to/local/directory b2://your-bucket --max-age <number>d --min-size <number>MB --threads <number>
```
