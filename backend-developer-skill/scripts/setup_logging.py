#!/usr/bin/env python3
"""
Logging and Monitoring Setup Script
"""

import sys
import argparse
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_logging_config(output_path: Path):
    # Express logging
    express_logger = """import winston from 'winston';

const { combine, timestamp, printf, errors, json } = winston.format;

const logFormat = printf(({ level, message, timestamp, stack }) => {
    return `${timestamp} [${level}]: ${stack || message}`;
});

const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: combine(
        errors({ stack: true }),
        timestamp(),
        process.env.NODE_ENV === 'production' ? json() : logFormat
    ),
    defaultMeta: { service: process.env.SERVICE_NAME || 'api-service' },
    transports: [
        new winston.transports.Console(),
        new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/combined.log' }),
    ],
});

if (process.env.NODE_ENV !== 'production') {
    logger.add(
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.simple()
            ),
        })
    );
}

export default logger;
"""

    # FastAPI logging
    fastapi_logger = """import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                "logs/app.log",
                maxBytes=10485760,
                backupCount=5,
                encoding="utf-8"
            )
        ]
    )

    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)

    return logging.getLogger(settings.PROJECT_NAME)
"""

    # Monitoring setup
    monitoring_content = """import { Request, Response, NextFunction } from 'express';
import logger from './logger';

export const requestLogger = (req: Request, res: Response, next: NextFunction) => {
    const start = Date.now();

    res.on('finish', () => {
        const duration = Date.now() - start;
        logger.info({
            method: req.method,
            url: req.url,
            status: res.statusCode,
            duration: `${duration}ms`,
            userAgent: req.get('user-agent'),
            ip: req.ip,
        });
    });

    next();
};

export const healthCheck = (req: Request, res: Response) => {
    const health = {
        uptime: process.uptime(),
        message: 'OK',
        timestamp: Date.now(),
        checks: {
            database: true,
            cache: true,
            externalServices: true,
        },
    };

    res.json(health);
};
"""

    src_path = output_path / 'src'
    src_path.mkdir(parents=True, exist_ok=True)

    with open(src_path / 'utils' / 'logger.ts', 'w') as f:
        f.write(express_logger)
    with open(src_path / 'middleware' / 'requestLogger.ts', 'w') as f:
        f.write(monitoring_content)

    app_path = output_path / 'app'
    app_path.mkdir(parents=True, exist_ok=True)
    with open(app_path / 'core' / 'logging.py', 'w') as f:
        f.write(fastapi_logger)


def main():
    parser = argparse.ArgumentParser(description='Setup logging and monitoring')
    parser.add_argument('--output', default='.', help='Output directory')
    args = parser.parse_args()

    output_path = Path(args.output)

    try:
        create_logging_config(output_path)
        logger.info("✓ Logging and monitoring setup complete")
    except Exception as e:
        logger.error(f"Error setting up logging: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
