# Example: Good Pull Request Description

## Summary
Implement exponential backoff retry logic for failed payment transactions to reduce manual recovery time from 24 hours to 5 minutes. This improves customer experience and reduces support overhead for failed checkout attempts.

## Context
Currently, failed payment transactions require manual intervention and aren't automatically retried. This leads to:
- Lost sales for customers who don't manually retry
- High support volume for payment failures
- Degraded customer experience

Competitors implement automatic retry logic with configurable backoff strategies. This change brings us to industry standard.

Related: Closes #2341, relates to #1999

## Implementation
Added a new `RetryManager` class that:
- Tracks failed transactions with exponential backoff (1s, 2s, 4s, 8s, max 5 attempts)
- Stores retry state in a new `payment_retries` table
- Runs retry attempts via a scheduled background job (every 30 seconds)
- Logs all retry attempts for debugging

The `PaymentService` now delegates to `RetryManager` for handling failed transactions. When a payment fails, it's automatically queued for retry rather than failing immediately.

Key architectural decisions:
- **Database table vs. queue**: Chose database for persistence and query-ability rather than Redis queue (allows retry history/analytics)
- **Exponential backoff strategy**: Standard approach to prevent thundering herd on downstream payment processor
- **5-minute max wait**: Balances customer experience with processor load; informed by competitor benchmarking

## Files Changed (Review Priority)
- **Core Logic** (start here):
  - `src/payments/RetryManager.ts` – New retry logic with exponential backoff calculation
  - `src/payments/PaymentService.ts` – Updated to queue failed payments for retry
  - `src/jobs/ProcessPaymentRetries.ts` – Background job that executes retries
- **Data Layer**:
  - `migrations/001_add_payment_retries_table.ts` – Schema for retry tracking
  - `src/models/PaymentRetry.ts` – ORM model
- **Testing**:
  - `tests/payments/RetryManager.test.ts` – Unit tests for backoff calculation and state management
  - `tests/payments/PaymentService.test.ts` – Integration tests with RetryManager
  - `tests/jobs/ProcessPaymentRetries.test.ts` – Job execution and timing tests
- **Configuration**:
  - `.env.example` – New retry configuration variables
  - `src/config/payment.ts` – Retry strategy configuration

## Testing
To verify these changes:

1. **Unit tests**: `pnpm test payments retry`
   - Tests exponential backoff calculation
   - Tests retry state transitions
   - Tests max retry limit

2. **Integration tests**: `pnpm test payments integration`
   - Tests PaymentService queuing failed payments
   - Tests job processing retries correctly
   - Tests edge cases (job crashes, duplicate processing)

3. **Manual testing**:
   - Create a test payment with a card that always fails (use test card 4000000000000002)
   - Observe the transaction appears in retry queue
   - Wait for background job to run (30 seconds)
   - Verify retry attempt was made and logged
   - Check database for retry history

4. **Load testing**:
   - Simulate 100 concurrent failed payments
   - Verify job processes them without errors
   - Monitor database/processor load during retry window

## Risk Assessment
- **Breaking changes**: None. This is purely additive; failed payments now auto-retry instead of failing immediately.
- **Performance impact**: Minimal. New background job runs every 30 seconds for <1ms per existing retry.
- **Data migration**: One migration required to create `payment_retries` table. Rollback is safe (just drops table).
- **Backwards compatible**: Yes. Existing payment flow unchanged; only adds automatic retry layer.
- **Concerns**:
  - If payment processor has downtime, retries will continue for up to 5 minutes (acceptable per stakeholder feedback)
  - Potential duplicate charges if payment processor doesn't handle idempotency properly (mitigated by existing idempotency key implementation)

## Additional Notes
- Retry strategy (backoff timing, max attempts) can be configured in `config/payment.ts`
- All retries are logged with timestamps for debugging and analytics
- Database queries are indexed on `status` and `next_retry_at` for efficient job querying
