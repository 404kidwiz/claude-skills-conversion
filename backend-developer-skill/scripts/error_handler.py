#!/usr/bin/env python3
"""
Error Handler Setup Script
"""

import sys
import argparse
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_express_error_handler(output_path: Path):
    utils_content = """export class AppError extends Error {
    constructor(
        public statusCode: number,
        public message: string,
        public isOperational = true,
        public stack = ''
    ) {
        super(message);
        Object.setPrototypeOf(this, AppError.prototype);
        Error.captureStackTrace(this, this.constructor);
        this.stack = stack;
    }
}

export class BadRequestError extends AppError {
    constructor(message: string = 'Bad Request') {
        super(400, message);
    }
}

export class UnauthorizedError extends AppError {
    constructor(message: string = 'Unauthorized') {
        super(401, message);
    }
}

export class ForbiddenError extends AppError {
    constructor(message: string = 'Forbidden') {
        super(403, message);
    }
}

export class NotFoundError extends AppError {
    constructor(message: string = 'Resource not found') {
        super(404, message);
    }
}

export class ConflictError extends AppError {
    constructor(message: string = 'Conflict') {
        super(409, message);
    }
}

export class ValidationError extends AppError {
    constructor(message: string = 'Validation failed') {
        super(422, message);
    }
}

export class InternalServerError extends AppError {
    constructor(message: string = 'Internal Server Error') {
        super(500, message);
    }
}
"""

    handler_content = """import { Request, Response, NextFunction } from 'express';
import { AppError } from '../utils/errors';
import logger from '../utils/logger';

export const errorHandler = (
    err: Error | AppError,
    req: Request,
    res: Response,
    next: NextFunction
): void => {
    if (err instanceof AppError) {
        logger.error(`${err.statusCode} - ${err.message} - ${req.originalUrl} - ${req.method}`);

        res.status(err.statusCode).json({
            status: 'error',
            statusCode: err.statusCode,
            message: err.message,
            ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
        });
        return;
    }

    logger.error(`${err.message} - ${req.originalUrl} - ${req.method}`);

    res.status(500).json({
        status: 'error',
        statusCode: 500,
        message: 'Internal Server Error',
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
    });
};

export const notFoundHandler = (
    req: Request,
    res: Response,
    next: NextFunction
): void => {
    const error = new Error(`Not Found - ${req.originalUrl}`);
    res.status(404).json({
        status: 'error',
        statusCode: 404,
        message: error.message,
    });
};
"""

    logger_content = """import pino from 'pino';

const logger = pino({
    level: process.env.LOG_LEVEL || 'info',
    transport: process.env.NODE_ENV === 'development'
        ? {
              target: 'pino-pretty',
              options: {
                  colorize: true,
                  translateTime: 'HH:MM:ss Z',
                  ignore: 'pid,hostname',
              },
          }
        : undefined,
});

export default logger;
"""

    utils_path = output_path / 'src' / 'utils'
    utils_path.mkdir(parents=True, exist_ok=True)

    with open(utils_path / 'errors.ts', 'w') as f:
        f.write(utils_content)
    with open(utils_path / 'logger.ts', 'w') as f:
        f.write(logger_content)

    middleware_path = output_path / 'src' / 'middleware'
    middleware_path.mkdir(parents=True, exist_ok=True)
    with open(middleware_path / 'errorHandler.ts', 'w') as f:
        f.write(handler_content)


def create_fastapi_error_handler(output_path: Path):
    exceptions_content = """from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


class BadRequestException(AppException):
    def __init__(self, detail: Any = "Bad Request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: Any = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(AppException):
    def __init__(self, detail: Any = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(AppException):
    def __init__(self, detail: Any = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(AppException):
    def __init__(self, detail: Any = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationException(AppException):
    def __init__(self, detail: Any = "Validation failed"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "statusCode": exc.status_code, "detail": exc.detail},
        headers=exc.headers,
    )
"""

    core_path = output_path / 'app' / 'core'
    core_path.mkdir(parents=True, exist_ok=True)
    with open(core_path / 'exceptions.py', 'w') as f:
        f.write(exceptions_content)


def main():
    parser = argparse.ArgumentParser(description='Create error handler')
    parser.add_argument('framework', choices=['express', 'fastapi'],
                        help='Framework to use')
    parser.add_argument('--output', default='.', help='Output directory')
    args = parser.parse_args()

    output_path = Path(args.output)

    try:
        if args.framework == 'express':
            create_express_error_handler(output_path)
        elif args.framework == 'fastapi':
            create_fastapi_error_handler(output_path)

        logger.info(f"✓ Created error handler for {args.framework}")
    except Exception as e:
        logger.error(f"Error creating error handler: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
