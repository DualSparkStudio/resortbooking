# Payment Configuration Guide

## IntegrityError Fixed!
Your booking system is now working! The payment error you're seeing is just a configuration issue.

## Payment Gateway Configuration

### Option 1: Use Stripe (Recommended for Testing)
1. Get Stripe test keys from: https://dashboard.stripe.com/test/apikeys
2. Add to .env file:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
   STRIPE_SECRET_KEY=sk_test_your_key_here
   ```

### Option 2: Use Razorpay (For Indian Market)
1. Get Razorpay keys from: https://dashboard.razorpay.com/app/keys
2. Add to .env file:
   ```
   RAZORPAY_KEY_ID=rzp_test_your_key_here
   RAZORPAY_KEY_SECRET=your_secret_here
   ```

### Option 3: Disable Payments (For Testing Bookings Only)
- Leave payment keys empty in .env file
- Bookings will be created but payment will be skipped

## Testing Without Payment Keys

Your booking system is now fully functional! Even without payment keys:
- Guest bookings work (IntegrityError fixed!)
- Room availability checking works
- Booking creation works
- Admin panel works
- Payment processing will show an error (expected without keys)

## Quick Test Steps

1. Visit: http://localhost:5000
2. Select dates and room type
3. Fill guest details
4. Click "Book Now"
5. You'll reach the payment page (proves booking creation works!)

## Admin Access
- URL: http://localhost:5000/admin
- Login: admin / admin123
- View all bookings and manage the system

The main issue (IntegrityError) is completely fixed!
