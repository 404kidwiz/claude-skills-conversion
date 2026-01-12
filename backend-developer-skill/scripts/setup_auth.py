#!/usr/bin/env python3
"""
Authentication/Authorization Setup Script
Supports JWT, OAuth2, Session-based auth
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AuthSetup:
    """Authentication and authorization setup utility"""

    def __init__(self, framework: str, auth_type: str, config: Dict):
        self.framework = framework.lower()
        self.auth_type = auth_type.lower()
        self.config = config

        if self.framework not in ['express', 'fastapi', 'django', 'spring']:
            raise ValueError(f"Unsupported framework: {framework}")

        if self.auth_type not in ['jwt', 'oauth2', 'session']:
            raise ValueError(f"Unsupported auth type: {auth_type}")

    def setup(self):
        """Main setup method"""
        logger.info(f"Setting up {self.auth_type} authentication for {self.framework}")

        if self.framework == 'express':
            self._setup_express_auth()
        elif self.framework == 'fastapi':
            self._setup_fastapi_auth()
        elif self.framework == 'django':
            self._setup_django_auth()
        elif self.framework == 'spring':
            self._setup_spring_auth()

        logger.info("✓ Authentication setup complete!")

    def _setup_express_auth(self):
        """Setup Express authentication"""
        output_path = Path(self.config.get('output_path', 'src'))

        if self.auth_type == 'jwt':
            self._create_express_jwt_middleware(output_path)
            self._create_express_auth_utils(output_path)

        elif self.auth_type == 'oauth2':
            self._create_express_oauth2_config(output_path)
            self._create_express_oauth2_routes(output_path)

        elif self.auth_type == 'session':
            self._create_express_session_config(output_path)
            self._create_express_auth_routes(output_path)

    def _create_express_jwt_middleware(self, output_path: Path):
        """Create Express JWT middleware"""
        content = """import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { UnauthorizedError } from '../utils/errors';

export interface AuthRequest extends Request {
    user?: {
        id: number;
        email: string;
        role: string;
    };
}

export const authenticate = (
    req: AuthRequest,
    res: Response,
    next: NextFunction
) => {
    try {
        const token = req.headers.authorization?.split(' ')[1];

        if (!token) {
            throw new UnauthorizedError('No token provided');
        }

        const decoded = jwt.verify(
            token,
            process.env.JWT_SECRET || 'your-secret-key'
        ) as any;

        req.user = decoded;
        next();
    } catch (error) {
        next(new UnauthorizedError('Invalid token'));
    }
};

export const authorize = (...roles: string[]) => {
    return (req: AuthRequest, res: Response, next: NextFunction) => {
        if (!req.user) {
            return next(new UnauthorizedError('Not authenticated'));
        }

        if (roles.length && !roles.includes(req.user.role)) {
            return next(new UnauthorizedError('Not authorized'));
        }

        next();
    };
};
"""

        middleware_path = output_path / 'middleware'
        middleware_path.mkdir(parents=True, exist_ok=True)
        with open(middleware_path / 'auth.ts', 'w') as f:
            f.write(content)

    def _create_express_auth_utils(self, output_path: Path):
        """Create Express auth utilities"""
        content = """import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';

export const hashPassword = async (password: string): Promise<string> => {
    const salt = await bcrypt.genSalt(10);
    return bcrypt.hash(password, salt);
};

export const comparePassword = async (
    password: string,
    hash: string
): Promise<boolean> => {
    return bcrypt.compare(password, hash);
};

export const generateToken = (payload: object): string => {
    return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
};

export const verifyToken = (token: string): any => {
    return jwt.verify(token, JWT_SECRET);
};
"""

        utils_path = output_path / 'utils'
        utils_path.mkdir(parents=True, exist_ok=True)
        with open(utils_path / 'auth.ts', 'w') as f:
            f.write(content)

    def _setup_fastapi_auth(self):
        """Setup FastAPI authentication"""
        output_path = Path(self.config.get('output_path', 'app'))

        if self.auth_type == 'jwt':
            self._create_fastapi_jwt_dependency(output_path)
            self._create_fastapi_auth_utils(output_path)

        elif self.auth_type == 'oauth2':
            self._create_fastapi_oauth2_config(output_path)
            self._create_fastapi_oauth2_router(output_path)

    def _create_fastapi_jwt_dependency(self, output_path: Path):
        """Create FastAPI JWT dependency"""
        content = """from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta

from app.core.config import settings

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"id": user_id, "email": payload.get("email")}


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
"""

        deps_path = output_path / 'core' / 'deps.py'
        deps_path.parent.mkdir(parents=True, exist_ok=True)
        with open(deps_path, 'w') as f:
            f.write(content)

    def _setup_django_auth(self):
        """Setup Django authentication"""
        output_path = Path(self.config.get('output_path', 'config'))

        if self.auth_type == 'jwt':
            self._create_django_jwt_views(output_path)
            self._create_django_jwt_serializers(output_path)

    def _create_django_jwt_views(self, output_path: Path):
        """Create Django JWT views"""
        content = """from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = User.objects.filter(email=email).first()

    if not user or not user.check_password(password):
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'email': user.email,
            'role': user.role,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        email=email,
        password=password
    )

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'email': user.email,
            'role': user.role,
        }
    }, status=status.HTTP_201_CREATED)
"""

        auth_path = output_path / 'auth'
        auth_path.mkdir(parents=True, exist_ok=True)
        with open(auth_path / 'views.py', 'w') as f:
            f.write(content)

    def _setup_spring_auth(self):
        """Setup Spring Boot authentication"""
        output_path = Path(self.config.get('output_path', 'src/main/java/com/example'))

        if self.auth_type == 'jwt':
            self._create_spring_security_config(output_path)
            self._create_spring_jwt_utils(output_path)

    def _create_spring_security_config(self, output_path: Path):
        """Create Spring Security configuration"""
        content = """package com.example.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/api/v1/health").permitAll()
                .anyRequest().authenticated()
            );

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
"""

        config_path = output_path / 'config'
        config_path.mkdir(parents=True, exist_ok=True)
        with open(config_path / 'SecurityConfig.java', 'w') as f:
            f.write(content)

    def _create_fastapi_auth_utils(self, output_path: Path):
        """Create FastAPI auth utilities"""
        content = """from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
"""

        utils_path = output_path / 'core' / 'security.py'
        utils_path.parent.mkdir(parents=True, exist_ok=True)
        with open(utils_path, 'w') as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(description='Setup authentication/authorization')
    parser.add_argument('framework', choices=['express', 'fastapi', 'django', 'spring'],
                        help='Framework to use')
    parser.add_argument('auth_type', choices=['jwt', 'oauth2', 'session'],
                        help='Authentication type')
    parser.add_argument('--config', help='Path to config file (JSON)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {args.config}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file: {args.config}")
            sys.exit(1)

    try:
        auth_setup = AuthSetup(args.framework, args.auth_type, config)
        auth_setup.setup()
    except Exception as e:
        logger.error(f"Error setting up authentication: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
