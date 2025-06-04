// frontend/components/RepoSlashInput.tsx
import React from 'react';

export interface RepoSlashInputProps {
    repoOwner: string;
    repoName: string;
    gradientFrom: string;
    gradientTo: string;
    backgroundColor: string;
    placeholderOwner?: string;
    placeholderName?: string;
    className?: string;
    onOwnerChange: (value: string) => void;
    onNameChange: (value: string) => void;
    height?: string;
    width?: string;
    fontSize?: string;
    fontWeight?: number | string;
    borderSize?: number;
}

const RepoSlashInput: React.FC<RepoSlashInputProps> = ({
    repoOwner,
    repoName,
    gradientFrom,
    gradientTo,
    backgroundColor,
    placeholderOwner = 'owner',
    placeholderName = 'repo',
    className = '',
    onOwnerChange,
    onNameChange,
    height = '56px',
    width = '100%',
    fontSize = '1rem',
    fontWeight = 500,
    borderSize = 2,
}) => {
    const baseRadius = '0.5rem';
    const borderSizePx = borderSize;
    const innerRadius = `calc(${baseRadius} - ${borderSizePx}px)`;
    const innerHeight = `calc(${height} - ${borderSizePx * 2}px)`;

    const outerStyle: React.CSSProperties = {
        background: `linear-gradient(to right, ${gradientFrom}, ${gradientTo})`,
        padding: `${borderSizePx}px`,
        borderRadius: baseRadius,
        height: height,
        width: width,
    };

    const innerStyle: React.CSSProperties = {
        backgroundColor: backgroundColor,
        borderRadius: innerRadius,
        height: innerHeight,
        width: '100%',
    };

    const inputStyle: React.CSSProperties = {
        backgroundColor: 'transparent',
        border: 'none',
        outline: 'none',
        color: 'inherit',
        fontSize: fontSize,
        fontWeight: fontWeight,
        textAlign: 'center',
    };

    return (
        <div className={`rounded-lg ${className}`} style={outerStyle}>
            <div className="flex items-center px-4" style={innerStyle}>
                <input
                    type="text"
                    value={repoOwner}
                    placeholder={placeholderOwner}
                    onChange={(e) => onOwnerChange(e.target.value)}
                    style={inputStyle}
                    className="flex-1 placeholder-gray-400"
                />
                <span className="px-2 select-none" style={inputStyle}>/</span>
                <input
                    type="text"
                    value={repoName}
                    placeholder={placeholderName}
                    onChange={(e) => onNameChange(e.target.value)}
                    style={inputStyle}
                    className="flex-1 placeholder-gray-400"
                />
            </div>
        </div>
    );
};

export default RepoSlashInput;