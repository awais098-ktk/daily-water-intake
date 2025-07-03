# Cloud Sync

This feature enables users to synchronize their water intake data across multiple devices and create backups using cloud storage services.

## Implementation Details

### Supported Services
- Google Drive
- Dropbox
- OneDrive (future)
- Custom WebDAV (future)

### Sync Functionality
- Automatic background sync
- Manual sync option
- Conflict resolution strategies
- Offline mode with sync queue

### Backup System
- Scheduled automatic backups
- Manual backup creation
- Backup restoration
- Version history

### User Interface
- Cloud service connection in settings
- Sync status indicators
- Backup management interface
- Restore from backup option

## Dependencies
- `google-auth-oauthlib` for Google Drive
- `dropbox` SDK for Dropbox
- `requests` for API calls
- `sqlalchemy` for database operations

## Files
- `cloud_sync.py`: Main sync controller
- `google_drive.py`: Google Drive implementation
- `dropbox_sync.py`: Dropbox implementation
- `sync_manager.js`: Frontend JavaScript for sync status
- `backup_manager.py`: Backup creation and restoration
- `cloud_settings.html`: Cloud settings template

## Integration Points
- User authentication system
- Database models
- Settings page
- App initialization

## Testing
1. Test sync with various data changes
2. Test conflict resolution
3. Test backup and restore functionality
4. Verify offline operation

## Future Enhancements
- End-to-end encryption
- Selective sync options
- Cross-platform sync (mobile apps)
- Shared family accounts
