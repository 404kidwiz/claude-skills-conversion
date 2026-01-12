#!/usr/bin/env python3
"""
Create Input Validation Middleware Script
"""

import sys
import argparse
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_express_validation_middleware(output_path: Path):
    content = """import { Request, Response, NextFunction } from 'express';
import { body, param, query, validationResult, ValidationChain } from 'express-validator';

export const handleValidationErrors = (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({
            errors: errors.array().map(err => ({
                field: err.param,
                message: err.msg,
            })),
        });
    }
    next();
};

export const validateBody = (fields: ValidationChain[]) => [
    ...fields,
    handleValidationErrors,
];

export const validateParams = (fields: ValidationChain[]) => [
    ...fields,
    handleValidationErrors,
];

export const validateQuery = (fields: ValidationChain[]) => [
    ...fields,
    handleValidationErrors,
];

export const registerValidationRules: ValidationChain[] = [
    body('email')
        .isEmail()
        .normalizeEmail()
        .withMessage('Please provide a valid email'),
    body('password')
        .isLength({ min: 8 })
        .withMessage('Password must be at least 8 characters long')
        .matches(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])/)
        .withMessage('Password must contain uppercase, lowercase, number, and special character'),
    body('name')
        .trim()
        .isLength({ min: 2, max: 50 })
        .withMessage('Name must be between 2 and 50 characters'),
];

export const loginValidationRules: ValidationChain[] = [
    body('email')
        .isEmail()
        .normalizeEmail()
        .withMessage('Please provide a valid email'),
    body('password')
        .notEmpty()
        .withMessage('Password is required'),
];
"""
    with open(output_path / 'middleware' / 'validation.ts', 'w') as f:
        f.write(content)


def create_fastapi_validation_middleware(output_path: Path):
    content = """from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

class UserBase(BaseSchema):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain an uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain a lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain a digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain a special character')
        return v

class UserUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class PaginatedResponse(BaseSchema):
    total: int
    page: int
    page_size: int
    items: list
"""
    with open(output_path / 'schemas' / 'user.py', 'w') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description='Create validation middleware')
    parser.add_argument('framework', choices=['express', 'fastapi', 'django'],
                        help='Framework to use')
    parser.add_argument('--output', default='.', help='Output directory')
    args = parser.parse_args()

    output_path = Path(args.output)

    try:
        if args.framework == 'express':
            create_express_validation_middleware(output_path)
        elif args.framework == 'fastapi':
            create_fastapi_validation_middleware(output_path)

        logger.info(f"✓ Created validation middleware for {args.framework}")
    except Exception as e:
        logger.error(f"Error creating validation middleware: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
