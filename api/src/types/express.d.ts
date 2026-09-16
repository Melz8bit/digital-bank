declare global {
  namespace Express {
    interface Request {
      parentId?: string;
    }
  }
}

export {};
