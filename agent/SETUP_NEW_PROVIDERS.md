# 🚀 Setting Up New Travel Providers

This guide will help you set up the new **Google Flights** and **Booking.com** providers via RapidAPI to enhance your Constellation Travel system.

## 📋 Prerequisites

- Python 3.8+
- Existing Constellation Travel setup
- RapidAPI account (free tier available)

## 🔑 RapidAPI Setup

### 1. Create RapidAPI Account
1. Go to [RapidAPI.com](https://rapidapi.com)
2. Sign up for a free account
3. Verify your email

### 2. Subscribe to APIs

#### Google Flights API
1. Search for "Google Flights Search" on RapidAPI
2. Subscribe to the free tier (usually 100 requests/month)
3. Copy your API key from the "X-RapidAPI-Key" field

#### Booking.com API
1. Search for "Booking.com" on RapidAPI
2. Subscribe to the free tier (usually 100 requests/month)
3. Copy your API key from the "X-RapidAPI-Key" field

## 🌍 Environment Variables

Add these to your environment (`.env` file or system environment):

```bash
# Google Flights via RapidAPI
RAPIDAPI_GOOGLE_FLIGHTS_KEY=your_google_flights_api_key_here
RAPIDAPI_GOOGLE_FLIGHTS_HOST=google-flights-search.p.rapidapi.com

# Booking.com via RapidAPI  
RAPIDAPI_BOOKING_KEY=your_booking_com_api_key_here
RAPIDAPI_BOOKING_HOST=booking-com.p.rapidapi.com

# Your existing keys
AMADEUS_API_KEY=your_existing_amadeus_key
AMADEUS_API_SECRET=your_existing_amadeus_secret
RAPIDAPI_KIWI_KEY=your_existing_kiwi_key
```

## 🧪 Testing the New Providers

### Individual Provider Tests

Test each provider separately first:

```bash
# Test Google Flights
cd agent
python smoke_test_google_flights.py

# Test Booking.com
python smoke_test_booking_com.py
```

### Combined System Test

Test the entire system with all providers:

```bash
# Test all providers together
cd agent
python smoke_test_combined.py
```

### Full System Test

Test the complete travel deal agent:

```bash
# Test the main agent with all providers
cd agent
python travel_deal_agent.py --config ../config/request.json
```

## 🔍 Expected Results

### Google Flights
- ✅ API connection successful
- ✅ Flight data normalized correctly
- ✅ Price, carrier, and route information extracted
- ✅ Error handling for missing/invalid data

### Booking.com
- ✅ API connection successful
- ✅ Hotel data normalized correctly
- ✅ Price, stars, and board information extracted
- ✅ Filtering by minimum stars working

### Combined System
- ✅ Multiple providers working together
- ✅ Duplicate removal working
- ✅ Deal matching logic working
- ✅ Fallback strategies working

## 🚨 Troubleshooting

### Common Issues

#### "Missing API Key" Errors
- Check environment variables are set correctly
- Restart your terminal/IDE after setting variables
- Verify API keys are valid in RapidAPI dashboard

#### "API Request Failed" Errors
- Check your internet connection
- Verify API subscription is active
- Check rate limits in RapidAPI dashboard
- Some APIs may have geographic restrictions

#### "No Results Found" Errors
- This is normal for some routes/dates
- Try different dates or destinations
- Check if the API supports your search parameters

### Debug Mode

Enable debug logging by setting:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/agent"
export DEBUG=1
```

## 📊 API Rate Limits

### Free Tier Limits
- **Google Flights**: Usually 100 requests/month
- **Booking.com**: Usually 100 requests/month
- **Amadeus**: Varies by plan
- **Kiwi**: Varies by plan

### Monitoring Usage
- Check RapidAPI dashboard for usage statistics
- Monitor your application logs for rate limit errors
- Consider upgrading plans for production use

## 🚀 Production Deployment

### Environment Setup
1. Use production API keys (higher rate limits)
2. Set up proper logging and monitoring
3. Implement rate limiting and retry logic
4. Use environment-specific configuration files

### Monitoring
- Track API response times
- Monitor success/failure rates
- Set up alerts for API failures
- Log all search requests and results

## 🔄 Updating Existing Deployments

If you're updating an existing deployment:

1. **Backup current configuration**
2. **Test new providers in staging**
3. **Update environment variables**
4. **Deploy new code**
5. **Monitor for any issues**
6. **Rollback if necessary**

## 📚 Additional Resources

- [RapidAPI Documentation](https://docs.rapidapi.com/)
- [Google Flights API Docs](https://rapidapi.com/letscrape-6bRBa3QguO5/api/google-flights-search/)
- [Booking.com API Docs](https://rapidapi.com/3b-data-3b-data-default/api/booking-com/)
- [Constellation Travel GitHub](your-repo-url)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review API documentation
3. Check RapidAPI status page
4. Open an issue in the project repository

---

**Happy Travel Searching! ✈️🏨**



