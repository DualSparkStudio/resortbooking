# Razorpay Integration Setup Guide

## Overview
This application now supports both Stripe and Razorpay payment gateways, allowing customers to choose their preferred payment method.

## Prerequisites
1. Razorpay account (Sign up at: https://razorpay.com/)
2. Valid Indian business registration (for live mode)

## Setup Instructions

### 1. Create Razorpay Account
- Go to https://razorpay.com/ and sign up
- Complete the account verification process
- Access your dashboard

### 2. Get API Keys
- Login to Razorpay Dashboard
- Go to Settings → API Keys
- Generate new API Key pair (Test mode for development)
- Copy the Key ID and Key Secret

### 3. Configure Environment Variables
Add the following to your environment variables or `.env` file:

```bash
# Razorpay Configuration
RAZORPAY_KEY_ID=rzp_test_your_key_id_here
RAZORPAY_KEY_SECRET=your_key_secret_here
```

**Important Notes:**
- Use `rzp_test_` keys for testing
- Use `rzp_live_` keys for production
- Keep the Key Secret secure and never expose it in frontend code

### 4. Currency Configuration
- Razorpay amounts are processed in **paise** (₹1 = 100 paise)
- The application automatically converts amounts to paise for processing
- Default currency is set to **INR** (Indian Rupees)

### 5. Payment Flow
1. Customer completes booking details
2. System creates a pending booking
3. Customer selects payment method (Stripe or Razorpay)
4. For Razorpay:
   - System creates Razorpay order
   - Customer redirected to Razorpay payment page
   - Multiple payment options available (UPI, Cards, Net Banking, Wallets)
   - Payment verification happens server-side
   - Booking confirmed on successful payment

### 6. Testing

#### Test Payment Methods
- **UPI**: Use test UPI IDs provided by Razorpay
- **Cards**: Use Razorpay test card numbers
- **Net Banking**: Test bank options available

#### Test Card Numbers (Razorpay Test Mode)
- **Success**: 4111 1111 1111 1111
- **Failure**: 4000 0000 0000 0002
- **CVV**: Any 3 digits
- **Expiry**: Any future date

### 7. Webhook Configuration (Optional)
For production, set up webhooks in Razorpay dashboard:
- Webhook URL: `https://yourdomain.com/webhook/razorpay`
- Events: `payment.captured`, `payment.failed`

### 8. Security Features
- Payment signature verification
- Server-side payment validation
- Secure order creation
- CSRF protection

### 9. Supported Payment Methods
- Credit/Debit Cards (Visa, Mastercard, RuPay, Amex)
- UPI (Google Pay, PhonePe, Paytm, etc.)
- Net Banking (All major banks)
- Wallets (Paytm, Mobikwik, etc.)
- EMI options
- Buy Now Pay Later (BNPL)

### 10. Go Live Checklist
1. ✅ Complete KYC verification in Razorpay dashboard
2. ✅ Switch to live API keys
3. ✅ Update webhook URLs
4. ✅ Test payment flows in live environment
5. ✅ Enable required payment methods
6. ✅ Configure settlement preferences

## Features Implemented

### Customer Features
- **Payment Method Selection**: Choose between Stripe and Razorpay
- **Multiple Payment Options**: Cards, UPI, Net Banking, Wallets
- **Mobile Optimized**: Responsive payment interface
- **Real-time Verification**: Instant payment confirmation
- **Secure Processing**: End-to-end encryption

### Admin Features
- **Payment Gateway Tracking**: View which gateway was used
- **Transaction IDs**: Access to payment and order IDs
- **Payment Status**: Real-time payment status updates
- **Reporting**: Filter bookings by payment gateway

### Technical Features
- **Dual Gateway Support**: Seamless switching between gateways
- **Database Integration**: Complete payment tracking
- **Error Handling**: Graceful failure management
- **Security**: Payment signature verification
- **Logging**: Comprehensive payment logging

## Troubleshooting

### Common Issues
1. **"Razorpay client not configured"**
   - Check if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are set
   - Verify the keys are correct

2. **Payment verification failed**
   - Ensure webhook signature verification is working
   - Check network connectivity
   - Verify order IDs match

3. **Currency issues**
   - Razorpay only supports INR for Indian businesses
   - Amounts must be in paise (multiply by 100)

### Support
- Razorpay Documentation: https://razorpay.com/docs/
- Integration Support: https://razorpay.com/support/
- API Reference: https://razorpay.com/docs/api/

## Migration from Stripe-only
The application maintains backward compatibility. Existing Stripe integrations continue to work alongside the new Razorpay integration. No changes needed for existing bookings. 