import React from 'react';
import type { Company } from '../types';
import { Lightbulb, Wrench, Globe, Flame } from 'lucide-react';
import './IntelligenceCard.css';

interface IntelligenceCardProps {
    company: Company;
}

const parseJSON = (jsonString?: string) => {
    if (!jsonString) return null;
    try {
        return JSON.parse(jsonString);
    } catch {
        return null;
    }
};

export const IntelligenceCard: React.FC<IntelligenceCardProps> = ({ company }) => {
    const maturity = parseJSON(company.maturity_info);
    const funding = parseJSON(company.funding_details);
    const hiring = parseJSON(company.hiring_signal);
    const opportunity = parseJSON(company.design_opportunity);
    const presence = parseJSON(company.public_presence_quality);

    if (!opportunity) return null;

    return (
        <div className="intelligence-card">
            <h4 className="intelligence-header">
                <Lightbulb size={18} className="text-yellow-500" />
                Design Intelligence
                {maturity?.stage && (
                    <span className="maturity-badge">
                        {maturity.stage}
                    </span>
                )}
            </h4>

            <div className="intelligence-grid">
                <div className="strategy-section">
                    <strong>Engagement Strategy</strong>
                    <p className="strategy-text">
                        "{company.engagement_recommendation || "No specific recommendation."}"
                    </p>
                </div>
                <div className="bottlenecks-section">
                    <strong>Bottlenecks</strong>
                    <ul className="bottlenecks-list">
                        {funding?.bottlenecks?.map((b: string, i: number) => (
                            <li key={i}>{b}</li>
                        )) || <li>None detected</li>}
                    </ul>
                </div>
            </div>

            <div className="intelligence-footer">
                {hiring?.hiring_velocity && (
                    <span className="footer-item">
                        <Wrench size={14} />
                        Hiring: <b>{hiring.hiring_velocity}</b>
                    </span>
                )}
                {presence?.quality_score && (
                    <span className="footer-item">
                        <Globe size={14} />
                        Web Presence: <b>{presence.quality_score}</b>
                    </span>
                )}
                {opportunity?.priority && (
                    <span className="footer-item">
                        <Flame size={14} />
                        Priority: <b className={opportunity.priority === 'High' ? 'priority-high' : ''}>{opportunity.priority}</b>
                    </span>
                )}
            </div>
        </div>
    );
};
