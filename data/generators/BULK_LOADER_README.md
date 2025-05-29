# Bulk Data Loader for Insight Journey

This script automates the process of loading all generated therapy session data into the Insight Journey backend system.

## 📋 What It Does

The bulk data loader performs the following operations for each user persona:

1. **Creates User Account**: Registers a new user with email format `{firstname}@insightsout.com`
2. **Login & Authentication**: Obtains auth token for API access
3. **Session Creation**: Creates 24 therapy sessions from the generated transcript files
4. **Session Analysis**: Runs OpenAI analysis on each session and stores results in Neo4j
5. **Data Verification**: Ensures all data is properly persisted

## 🗂️ Expected Directory Structure

```
data/generators/output/
├── Alex_Dr._Harper_Torres/
│   ├── session_01_20250501.txt
│   ├── session_02_20250508.txt
│   ├── session_03_20250515.txt
│   └── ... (24 sessions total)
├── Zoë_Dr._Serena_Bianchi/
│   ├── session_01_20250501.txt
│   └── ... (24 sessions total)
├── Omar_Malik_Johnson/
├── Lina_Riley_Chen/
├── Evan_Dr._Serena_Bianchi/
├── Priya_Dr._Harper_Torres/
├── Sam_Malik_Johnson/
├── Mei_Mara_Ortiz/
├── Diego_Dr._Harper_Torres/
└── Jasmine_Riley_Chen/
```

## 👥 Generated Users

The script will create the following 10 users:

| Name | Email | Password | Sessions |
|------|-------|----------|----------|
| Alex | alex@insightsout.com | Testuser123 | 24 |
| Zoë | zoë@insightsout.com | Testuser123 | 24 |
| Omar | omar@insightsout.com | Testuser123 | 24 |
| Lina | lina@insightsout.com | Testuser123 | 24 |
| Evan | evan@insightsout.com | Testuser123 | 24 |
| Priya | priya@insightsout.com | Testuser123 | 24 |
| Sam | sam@insightsout.com | Testuser123 | 24 |
| Mei | mei@insightsout.com | Testuser123 | 24 |
| Diego | diego@insightsout.com | Testuser123 | 24 |
| Jasmine | jasmine@insightsout.com | Testuser123 | 24 |

## 🚀 Usage

### Prerequisites

1. **Backend Running**: Ensure the Insight Journey backend is running on `localhost:8080`
2. **Python Dependencies**: Install required packages:
   ```bash
   pip install requests
   ```

### Basic Usage

```bash
# Load all users and their sessions
python bulk_data_loader.py

# Load specific users only
python bulk_data_loader.py --users Alex,Zoë

# Preview what would be done (dry run)
python bulk_data_loader.py --dry-run

# Use different API URL
python bulk_data_loader.py --base-url http://localhost:8080/api/v1
```

### Command Line Options

- `--users`: Comma-separated list of specific users to load (e.g., 'Alex,Zoë')
- `--dry-run`: Preview what would be done without making actual API calls
- `--base-url`: API base URL (default: http://localhost:8080/api/v1)

## 📊 Expected Output

The script provides detailed logging and statistics:

```
🚀 Starting bulk data loading for 10 users

============================================================
Processing User: Alex
Folder: Alex_Dr._Harper_Torres
Email: alex@insightsout.com
============================================================

✅ User created: Alex (ID: U_abc123...)
✅ Login successful

Found 24 session files for Alex
Processing session 1/24: session_01_20250501.txt
   ✅ Session 1 completed successfully
Processing session 2/24: session_02_20250508.txt
   ✅ Session 2 completed successfully
...

✅ User Alex completed in 45.2s
   Sessions: 24/24 (100.0% success)

================================================================================
🎯 BULK DATA LOADING COMPLETE
================================================================================

📊 SUMMARY STATISTICS:
   Total Duration: 450.0 seconds (7.5 minutes)
   Users Created: 10
   Users Failed: 0
   Sessions Created: 240
   Sessions Failed: 0
   Analyses Completed: 240
   Analyses Failed: 0
   Analysis Success Rate: 100.0%

👥 USER BREAKDOWN:
   Alex: 24/24 sessions (100.0%) in 45.2s
   Zoë: 24/24 sessions (100.0%) in 43.8s
   ...

📈 AVERAGES:
   Time per user: 45.0 seconds
   Sessions per user: 24.0

🎉 All users processed successfully!
```

## ⚡ Performance Considerations

- **Processing Time**: Expect ~45-60 seconds per user (including OpenAI analysis calls)
- **Total Time**: Full load of 10 users takes approximately 8-10 minutes
- **Rate Limiting**: Built-in delays to avoid overwhelming the API:
  - 0.5 seconds between sessions
  - 2 seconds between users
- **Memory Usage**: Processes one session at a time to minimize memory footprint

## 🛠️ Error Handling

The script includes comprehensive error handling:

- **Network Timeouts**: 30-60 second timeouts on API calls
- **Retry Logic**: Built-in delays and graceful failure handling
- **Progress Tracking**: Continues processing other users/sessions if one fails
- **Graceful Exit**: Ctrl+C interruption shows partial statistics
- **Detailed Logging**: All errors are logged with context

## 🔍 Dry Run Mode

Use `--dry-run` to preview operations without making actual API calls:

```bash
python bulk_data_loader.py --dry-run --users Alex
```

This will show you exactly what the script would do without creating any data.

## 📝 Session Data Format

Each session file contains:
- Session metadata (number, date, time, client, therapist)
- Full conversation transcript with timestamps
- Rich therapeutic dialogue for comprehensive analysis

Example session header:
```
Session 1/24
Date: May 01, 2025
Time: 10:00 AM
Client: Alex (Product Designer)
Professional: Dr. Harper Torres (Licensed Clinical Psychologist)

[10:00] Dr. Harper Torres: Hi Alex, it's great to see you again...
```

## 🔧 Troubleshooting

**Common Issues:**

1. **Backend Not Running**: Ensure the Insight Journey backend is running on the specified URL
2. **Permission Errors**: Check file permissions on the output directory
3. **Network Issues**: Verify API connectivity and firewall settings
4. **Memory Issues**: Use smaller user batches with `--users` if needed

**Debug Steps:**

1. Test with dry run first: `python bulk_data_loader.py --dry-run --users Alex`
2. Test single user: `python bulk_data_loader.py --users Alex`
3. Check backend logs for API errors
4. Verify session files exist and are readable

## 🎯 Success Criteria

After successful completion, you should have:

- 10 user accounts created
- 240 therapy sessions created (24 per user)
- 240 completed analyses with:
  - Emotions extracted
  - Beliefs identified
  - Action items generated
  - Challenges documented
  - Insights discovered
- All data persisted in Neo4j database
- Rich dataset for testing insights and analytics features

## 📈 Next Steps

After loading the data, you can:

1. **Test User Logins**: Use any of the created accounts to test the frontend
2. **Explore Insights**: View the generated insights dashboard
3. **Verify Analytics**: Check that charts and visualizations work with real data
4. **Performance Testing**: Use the dataset for load testing and optimization
5. **Feature Development**: Build new features with rich, realistic test data 