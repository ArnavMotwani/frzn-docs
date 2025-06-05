// frontend/components/RepoSlashCard.tsx
import React from 'react';
import { TrashIcon } from '@heroicons/react/24/outline';

export interface RepoSlashCardProps {
    repoOwner: string;
    repoName: string;
    gradientFrom: string;
    gradientTo: string;
    backgroundColor: string;
    showBackground?: boolean;
    className?: string;
    onClick?: () => void;
    onTrashClick?: () => void;
    height?: string;
    width?: string;
    fontSize?: string;
    fontWeight?: number | string;
    borderSize?: number;
}

const RepoSlashCard: React.FC<RepoSlashCardProps> = ({
    repoOwner,
    repoName,
    gradientFrom,
    gradientTo,
    backgroundColor,
    showBackground = true,
    className = '',
    onClick,
    onTrashClick,
    height = 'auto',
    width = 'auto',
    fontSize = '1rem',
    fontWeight = 500,
    borderSize = 2,
}) => {
    const baseRadius = '0.5rem';
    const borderPx = borderSize;
    const innerRadius = `calc(${baseRadius} - ${borderPx}px)`;

    const outerStyle: React.CSSProperties = {
        background: `linear-gradient(to right, ${gradientFrom}, ${gradientTo})`,
        padding: `${borderPx}px`,
        borderRadius: baseRadius,
        width: width,
        ...(height !== 'auto' ? { height: height } : {}),
    };

    const innerStyle: React.CSSProperties = {
        backgroundColor: backgroundColor,
        borderRadius: innerRadius,
        width: '100%',
        ...(height !== 'auto'
            ? { height: `calc(${height} - ${borderPx * 2}px)` }
            : {}),
    };

    const textStyle: React.CSSProperties = {
        background: `linear-gradient(to right, ${gradientFrom}, ${gradientTo})`,
        backgroundClip: 'text' as const,
        WebkitBackgroundClip: 'text' as const,
        WebkitTextFillColor: 'transparent' as const,
        display: 'inline-flex',
        alignItems: 'center',
        fontSize: fontSize,
        fontWeight: fontWeight,
    };

    if (!showBackground) {
        return (
            <span style={textStyle} className={className}>
                <span>{repoOwner}</span>
                <span className="mx-1">/</span>
                <span>{repoName}</span>
            </span>
        );
    }

    return (
        <div
            className={`rounded-lg ${className}`}
            style={outerStyle}
            onClick={onClick}
        >
            <div
                className="flex items-center justify-between px-3 py-2"
                style={innerStyle}
            >
                <span style={textStyle}>
                    <span>{repoOwner}</span>
                    <span className="mx-1">/</span>
                    <span>{repoName}</span>
                </span>

                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onTrashClick && onTrashClick();
                    }}
                    className="flex items-center justify-center p-1 rounded hover:bg-gray-200"
                    aria-label="Delete repository"
                >
                    <TrashIcon className="h-5 w-5 text-red-600" />
                </button>
            </div>
        </div>
    );
};

export default RepoSlashCard;