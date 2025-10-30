# ClauseBot API - Network Configuration

## Render Outbound IP Addresses

Network requests from the ClauseBot API service to external services (Airtable, Supabase, etc.) will originate from one of the following IP addresses:

### Current IP Addresses
- `44.229.227.142`
- `54.188.71.94` 
- `52.13.128.108`

### IP Ranges (Added October 27, 2025)
- `74.220.48.0/24` (74.220.48.1 - 74.220.48.254)
- `74.220.56.0/24` (74.220.56.1 - 74.220.56.254)

## External Service Configuration

### Airtable API Access
If Airtable has IP allowlisting enabled, add these IPs to your Airtable workspace security settings:

```
44.229.227.142
54.188.71.94
52.13.128.108
74.220.48.0/24
74.220.56.0/24
```

### Supabase Configuration
For Supabase IP restrictions (if enabled), add the same IP ranges to your project's network restrictions.

### Other External APIs
Any external service that requires IP allowlisting should include these Render outbound IPs.

## Security Considerations

1. **Shared IPs**: These IPs are shared across multiple Render services in the same region
2. **Region**: These IPs are specific to the Render region where ClauseBot API is deployed
3. **Changes**: Monitor Render announcements for IP range updates
4. **Fallback**: Always configure API keys and authentication as primary security

## Testing Connectivity

To verify outbound connectivity from ClauseBot API:

```bash
# Test from within the deployed service
curl -s https://httpbin.org/ip
# Should return one of the documented IP addresses

# Test Airtable connectivity
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.airtable.com/v0/YOUR_BASE_ID/YOUR_TABLE"
```

## Monitoring

Monitor these endpoints for IP-related issues:
- `/v1/quiz/health` - Will show Airtable connection status
- `/api/ready` - Shows dependency health including external services

## Update Schedule

- **Current IPs**: Active now
- **New IP Ranges**: Added October 27, 2025
- **Deprecation**: Monitor Render announcements for any IP changes

---
*Last Updated: 2025-10-11*  
*Service: clausebot-api.onrender.com*  
*Region: Render shared region*
