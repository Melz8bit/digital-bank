import z from 'zod';

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

export const CreateChildInputSchema = z.object({
  name: z.string().trim().min(1, 'Give your kid a name.'),
});
export type CreateChildInput = z.infer<typeof CreateChildInputSchema>;

export const TransactionInputSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('deposit'),
    amountCents: z.int().positive().max(10_000_000, 'That amount is too big.'),
    category: z.enum(['allowance', 'gift', 'chore', 'other']),
  }),
  z.object({
    type: z.literal('withdrawal'),
    amountCents: z.int().positive().max(10_000_000, 'That amount is too big.'),
    comment: z.string().trim().min(1, 'Tell us what you are spending it on.'),
  }),
]);
export type TransactionInput = z.infer<typeof TransactionInputSchema>;
