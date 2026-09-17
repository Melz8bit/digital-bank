import z from 'zod';

// zod validation schemas (SignupInput, DepositInput, WithdrawalInput, PinInput, ...) land here in Phase 1.

export const SignupInputSchema = z
  .object({
    email: z.email(),
    password: z.string().min(8),
    familyName: z.string().optional(),
    inviteCode: z.string().optional(),
  })
  .refine((data) => !!data.familyName !== !!data.inviteCode, {
    message: 'Either a family name or invite code is required.',
  });
export type SignupInput = z.infer<typeof SignupInputSchema>;

export const LoginInputSchema = z.object({
  email: z.email(),
  password: z.string().min(8),
});
export type LoginInput = z.infer<typeof LoginInputSchema>;

export const PinInputSchema = z.object({
  pin: z.string().regex(/^\d{4}$/, 'PIN must be exactly 4 digits.'),
});
export type PinInput = z.infer<typeof PinInputSchema>;
