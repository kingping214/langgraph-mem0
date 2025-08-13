# Security Guidelines

## Overview

This document outlines the security features and best practices implemented in the LangGraph + Mem0 integration demo. These security measures help protect against common vulnerabilities while maintaining functionality.

## Security Features Implemented

### 1. Input Validation and Sanitization

**Protection Against**: Injection attacks, XSS, malicious content
**Implementation**: 
- All user inputs are sanitized using HTML escaping
- Control characters and dangerous patterns are removed
- Maximum input length limits enforced (10,000 characters)
- Pattern matching to detect and remove potentially malicious scripts

**Configuration**:
```python
max_input_length = 10000  # Maximum input length
dangerous_patterns = [
    r'<script[^>]*>[\s\S]*?</script>',
    r'javascript:',
    r'on\w+\s*=',
    r'eval\s*\(',
    r'exec\s*\(',
]
```

### 2. Environment Variable Security

**Protection Against**: Configuration vulnerabilities, runtime failures
**Implementation**:
- Mandatory validation of all required environment variables
- Format validation for URLs and numeric values
- Secure error messages that don't expose system details

**Required Environment Variables**:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-0
OLLAMA_MODEL=nomic-embed-text:latest
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_DIMS=768
CHROMA_COLLECTION_NAME=test
CHROMA_DB_PATH=db
```

### 3. Error Handling and Information Disclosure Prevention

**Protection Against**: Information leakage, system enumeration
**Implementation**:
- Generic error messages to users
- Detailed errors logged securely for administrators
- Exception type logging without sensitive details

### 4. Memory Content Validation

**Protection Against**: Persistent malicious content, data corruption
**Implementation**:
- Content sanitization before storage
- Length limits for memory content (5,000 characters)
- Validation of retrieved memory content

### 5. Rate Limiting

**Protection Against**: DoS attacks, resource abuse
**Implementation**:
- Per-user rate limiting: 20 requests per minute, 100 per hour
- Automatic cleanup of old request records
- Graceful handling of rate limit violations

**Configuration**:
```python
rate_limits = {
    'requests_per_minute': 20,
    'requests_per_hour': 100
}
```

### 6. Security Logging and Monitoring

**Protection Against**: Undetected attacks, compliance violations
**Implementation**:
- Comprehensive security event logging
- Separate security log file (`security.log`)
- Structured logging with timestamps and severity levels

**Log Events**:
- Environment validation failures
- Input sanitization triggers
- Rate limit violations
- Memory validation failures
- Authentication/API errors

## Security Configuration

### Recommended Production Settings

1. **Environment Variables**:
   - Store API keys in secure secret management systems
   - Use environment-specific configuration files
   - Implement key rotation policies

2. **Rate Limiting**:
   - Adjust limits based on expected usage patterns
   - Consider implementing different limits for different user tiers
   - Monitor and alert on unusual traffic patterns

3. **Logging**:
   - Configure log rotation to prevent disk space issues
   - Send security logs to centralized monitoring systems
   - Set up alerts for critical security events

4. **Input Validation**:
   - Review and update dangerous patterns regularly
   - Consider implementing content scanning for specific use cases
   - Adjust length limits based on application requirements

### Additional Security Recommendations

1. **Network Security**:
   - Use HTTPS for all external API communications
   - Implement network firewalls and access controls
   - Consider VPN or private network access for Ollama

2. **Database Security**:
   - Encrypt ChromaDB data at rest
   - Implement backup encryption
   - Regular security updates for database dependencies

3. **Authentication and Authorization**:
   - Implement proper user authentication in production
   - Use unique, non-predictable user IDs
   - Consider multi-factor authentication for admin access

4. **Dependency Management**:
   - Regularly update dependencies for security patches
   - Use dependency scanning tools
   - Pin dependency versions in production

## Security Monitoring

### Key Metrics to Monitor

1. **Rate Limiting Events**: Track frequency and patterns
2. **Input Sanitization Triggers**: Monitor for attack attempts
3. **API Error Rates**: Detect potential abuse or system issues
4. **Memory Validation Failures**: Watch for data corruption attempts

### Alert Thresholds

- Multiple rate limit violations from single user: Immediate alert
- High frequency of input sanitization events: Investigation required
- Environment validation failures: Critical alert
- Unusual error patterns: Monitoring alert

## Incident Response

### Security Event Classifications

1. **Critical**: Environment compromise, data exfiltration attempts
2. **High**: Repeated attack patterns, rate limit abuse
3. **Medium**: Input sanitization triggers, validation failures
4. **Low**: Normal security events, routine monitoring

### Response Actions

1. **Immediate**: Block/rate limit offending users
2. **Short-term**: Review logs, assess impact
3. **Long-term**: Update security measures, improve monitoring

## Security Testing

### Recommended Tests

1. **Input Validation**: Test with malicious payloads
2. **Rate Limiting**: Verify limits are enforced correctly
3. **Error Handling**: Ensure no information leakage
4. **Environment Security**: Test with missing/invalid configurations

### Testing Tools

- Input fuzzing tools for validation testing
- Load testing tools for rate limit verification
- Static analysis tools for code security review
- Dependency vulnerability scanners

## Compliance Considerations

### Data Protection

- Memory content is stored locally in ChromaDB
- No data transmission to unauthorized third parties
- User data isolation through user_id segregation

### Privacy

- Conversation data is persisted locally
- No external data sharing beyond configured APIs
- User control over data through user_id management

## Security Updates

This security implementation should be reviewed and updated regularly:

- Monthly review of security logs and metrics
- Quarterly assessment of security measures effectiveness
- Annual security architecture review
- Immediate updates for critical vulnerabilities

## Contact

For security-related questions or to report vulnerabilities, please review the project's contribution guidelines and issue reporting process.