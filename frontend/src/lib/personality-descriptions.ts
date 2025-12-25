/**
 * Personality trait descriptions for interpreting assessment results.
 * Provides human-readable descriptions based on score levels.
 */

import { Language } from './i18n';

export type ScoreLevel = 'low' | 'moderate' | 'high';

export interface TraitDescription {
  name: string;
  low: string;
  moderate: string;
  high: string;
}

/**
 * Get the score level based on the Likert scale score (1-7)
 */
export function getScoreLevel(score: number): ScoreLevel {
  if (score < 3) return 'low';
  if (score <= 5) return 'moderate';
  return 'high';
}

/**
 * Trait descriptions in English
 */
const traitDescriptionsEN: Record<string, TraitDescription> = {
  extraversion: {
    name: 'Extraversion',
    low: 'You tend to be more reserved and prefer quieter, less stimulating environments. You may enjoy solitary activities and feel energized by spending time alone. You might prefer deep one-on-one conversations over large group gatherings.',
    moderate: 'You have a balanced approach to social interaction. You can enjoy both social gatherings and quiet time alone. You adapt well to different social situations and can be outgoing when needed while also appreciating solitude.',
    high: 'You are energetic, talkative, and thrive in social situations. You enjoy meeting new people and being the center of attention. You tend to feel energized by being around others and may seek out social activities frequently.',
  },
  agreeableness: {
    name: 'Agreeableness',
    low: 'You tend to be more competitive and skeptical of others\' intentions. You prioritize your own interests and may be more direct in expressing disagreement. You value honesty over diplomacy and aren\'t afraid to challenge others.',
    moderate: 'You balance cooperation with self-interest appropriately. You can be compassionate and helpful while also standing up for yourself when needed. You try to consider both your needs and others\' feelings in social situations.',
    high: 'You are compassionate, cooperative, and genuinely care about others\' well-being. You tend to trust others easily and prefer harmony over conflict. You are often willing to compromise and help others, sometimes even at your own expense.',
  },
  conscientiousness: {
    name: 'Conscientiousness',
    low: 'You tend to be more flexible and spontaneous in your approach to tasks. You may prefer to go with the flow rather than stick to rigid schedules. While you might sometimes struggle with organization, you adapt well to changing circumstances.',
    moderate: 'You have a balanced approach to organization and spontaneity. You can be disciplined when needed but also know when to relax your standards. You manage responsibilities reasonably well while maintaining flexibility.',
    high: 'You are organized, disciplined, and goal-oriented. You pay attention to details and prefer to plan ahead. You are reliable and tend to complete tasks thoroughly. Others often see you as responsible and dependable.',
  },
  neuroticism: {
    name: 'Emotional Stability',
    low: 'You tend to be emotionally stable and resilient. You handle stress well and don\'t get easily upset. You maintain a calm demeanor even in challenging situations and recover quickly from negative experiences.',
    moderate: 'You experience a normal range of emotions and can manage stress reasonably well. While you may sometimes feel anxious or upset, you generally maintain emotional balance and cope effectively with life\'s challenges.',
    high: 'You may experience emotions more intensely and be more sensitive to stress. You might worry more than others and experience mood fluctuations. Understanding and managing your emotional responses can help you navigate challenging situations.',
  },
  openness: {
    name: 'Openness to Experience',
    low: 'You tend to prefer familiar routines and practical approaches. You value tradition and conventional methods. You may be more comfortable with concrete, straightforward tasks rather than abstract or theoretical discussions.',
    moderate: 'You balance appreciation for tradition with openness to new experiences. You can enjoy both familiar routines and occasional novelty. You are reasonably curious while also valuing practical approaches.',
    high: 'You are curious, creative, and open to new ideas and experiences. You enjoy exploring abstract concepts and appreciate art, beauty, and imagination. You seek out variety and are willing to try unconventional approaches.',
  },
  honesty_humility: {
    name: 'Honesty-Humility',
    low: 'You may be more focused on status, wealth, and social recognition. You might be comfortable with flattery or bending rules to get ahead. You value success and material achievements.',
    moderate: 'You have a balanced view of material success and modest living. You appreciate recognition for your achievements while not being overly focused on status. You try to be fair and honest in most situations.',
    high: 'You are sincere, fair, and modest. You don\'t seek special treatment or try to manipulate others for personal gain. You are genuine in your interactions and prefer simplicity over luxury or status symbols.',
  },
};

/**
 * Trait descriptions in Korean
 */
const traitDescriptionsKR: Record<string, TraitDescription> = {
  extraversion: {
    name: '외향성',
    low: '조용하고 차분한 환경을 선호하시는 편입니다. 혼자만의 시간을 통해 에너지를 충전하며, 깊이 있는 일대일 대화를 즐기시는 경향이 있습니다. 대규모 모임보다는 소규모의 친밀한 만남을 더 편안하게 느끼실 수 있습니다.',
    moderate: '사회적 상호작용에 균형 잡힌 접근을 하시는 편입니다. 모임과 혼자만의 시간을 모두 즐기실 수 있으며, 다양한 사회적 상황에 잘 적응하십니다. 필요할 때는 외향적으로, 때로는 조용히 시간을 보내실 수 있습니다.',
    high: '활기차고 사교적이시며, 사람들과 함께하는 것을 즐기십니다. 새로운 사람들을 만나고 대화하는 것을 좋아하시며, 주변 사람들에게 에너지를 주는 편입니다. 사회적 활동을 통해 활력을 얻으시는 경향이 있습니다.',
  },
  agreeableness: {
    name: '우호성',
    low: '독립적이고 자신의 의견을 분명하게 표현하시는 편입니다. 타인의 의견에 쉽게 동조하기보다 비판적으로 생각하시며, 경쟁적인 상황에서도 자신의 입장을 잘 지키십니다.',
    moderate: '협력과 자기주장 사이에서 적절한 균형을 유지하시는 편입니다. 타인을 배려하면서도 필요할 때는 자신의 의견을 표현하실 수 있습니다. 상황에 따라 유연하게 대처하시는 경향이 있습니다.',
    high: '따뜻하고 배려심이 깊으시며, 타인의 감정에 공감을 잘 하시는 편입니다. 협력적이고 조화로운 관계를 중요시하시며, 주변 사람들을 돕는 것에서 보람을 느끼십니다. 갈등보다는 화합을 추구하시는 경향이 있습니다.',
  },
  conscientiousness: {
    name: '성실성',
    low: '유연하고 자유로운 방식을 선호하시는 편입니다. 엄격한 계획보다는 상황에 따라 적응하는 것을 편하게 느끼시며, 즉흥적인 결정에도 잘 대처하십니다. 변화하는 환경에 빠르게 적응하시는 장점이 있습니다.',
    moderate: '계획성과 유연성 사이에서 균형을 유지하시는 편입니다. 필요할 때는 체계적으로 일을 처리하면서도, 상황에 따라 계획을 조정하실 수 있습니다. 책임감 있게 일을 수행하시는 경향이 있습니다.',
    high: '체계적이고 목표 지향적이시며, 일을 꼼꼼하게 처리하시는 편입니다. 계획을 세우고 그에 따라 실행하는 것을 선호하시며, 주변에서 신뢰할 수 있는 사람으로 인식되는 경향이 있습니다. 책임감이 강하고 성실하십니다.',
  },
  neuroticism: {
    name: '정서적 안정성',
    low: '정서적으로 안정되어 있고 스트레스를 잘 관리하시는 편입니다. 어려운 상황에서도 침착함을 유지하시며, 부정적인 경험에서 빠르게 회복하시는 경향이 있습니다. 전반적으로 평온하고 안정적인 모습을 보이십니다.',
    moderate: '일반적인 범위의 감정 변화를 경험하시며, 스트레스를 적절히 관리하시는 편입니다. 때때로 걱정이나 불안을 느끼실 수 있지만, 대체로 감정적 균형을 유지하시며 삶의 도전에 효과적으로 대처하십니다.',
    high: '감정을 풍부하게 경험하시고 주변 환경에 민감하게 반응하시는 편입니다. 스트레스 상황에서 더 강하게 반응하실 수 있으며, 이러한 감수성은 때로 창의성과 공감 능력의 원천이 되기도 합니다. 자기 관리 기술을 활용하시면 더욱 도움이 될 수 있습니다.',
  },
  openness: {
    name: '개방성',
    low: '실용적이고 현실적인 접근을 선호하시는 편입니다. 검증된 방법과 익숙한 것을 중요시하시며, 구체적이고 명확한 것을 좋아하십니다. 안정적이고 예측 가능한 환경에서 편안함을 느끼시는 경향이 있습니다.',
    moderate: '전통과 새로운 경험 사이에서 균형을 유지하시는 편입니다. 익숙한 것을 편안하게 느끼면서도 때때로 새로운 것을 시도하는 것을 즐기십니다. 호기심이 있으면서도 현실적인 판단력을 갖추고 계십니다.',
    high: '호기심이 많고 창의적이시며, 새로운 아이디어와 경험에 열린 자세를 가지고 계십니다. 예술과 아름다움을 감상하고, 상상력이 풍부하십니다. 다양한 관점을 탐구하고 색다른 접근 방식을 시도하는 것을 즐기시는 경향이 있습니다.',
  },
  honesty_humility: {
    name: '정직-겸손',
    low: '성취와 인정을 중요시하시는 편입니다. 목표를 달성하기 위해 적극적으로 노력하시며, 사회적 지위나 물질적 성공에 가치를 두시는 경향이 있습니다. 자신의 능력과 성과에 자신감을 가지고 계십니다.',
    moderate: '물질적 성공과 겸손한 삶 사이에서 균형 잡힌 관점을 가지고 계십니다. 성취에 대한 인정을 받는 것을 좋아하시면서도, 지나치게 지위에 집착하지 않으십니다. 대부분의 상황에서 공정하고 정직하게 행동하시는 편입니다.',
    high: '진실하고 겸손하시며, 공정함을 중요시하시는 편입니다. 특별한 대우를 요구하거나 다른 사람을 이용하려 하지 않으십니다. 소박하고 진정성 있는 관계를 선호하시며, 물질적인 것보다 내면의 가치를 중시하시는 경향이 있습니다.',
  },
};

/**
 * Get trait description based on score and language
 */
export function getTraitDescription(
  trait: string,
  score: number,
  lang: Language
): { name: string; description: string; level: ScoreLevel } {
  const descriptions = lang === 'kr' ? traitDescriptionsKR : traitDescriptionsEN;
  const traitDesc = descriptions[trait];

  if (!traitDesc) {
    return {
      name: trait,
      description: '',
      level: 'moderate',
    };
  }

  const level = getScoreLevel(score);

  return {
    name: traitDesc.name,
    description: traitDesc[level],
    level,
  };
}

/**
 * Get all trait descriptions for a set of scores
 */
export function getAllTraitDescriptions(
  scores: Record<string, number>,
  lang: Language
): Array<{ trait: string; name: string; score: number; description: string; level: ScoreLevel }> {
  const traits = [
    'extraversion',
    'agreeableness',
    'conscientiousness',
    'neuroticism',
    'openness',
    'honesty_humility',
  ];

  return traits.map((trait) => {
    const score = scores[trait] || 4;
    const desc = getTraitDescription(trait, score, lang);
    return {
      trait,
      name: desc.name,
      score,
      description: desc.description,
      level: desc.level,
    };
  });
}

/**
 * Get a summary of the personality profile
 */
export function getProfileSummary(scores: Record<string, number>, lang: Language): string {
  const descriptions = getAllTraitDescriptions(scores, lang);
  const highTraits = descriptions.filter((d) => d.level === 'high');
  const lowTraits = descriptions.filter((d) => d.level === 'low');

  if (lang === 'kr') {
    let summary = '귀하의 성격 프로필 요약입니다.\n\n';

    if (highTraits.length > 0) {
      summary += `높은 수준을 보이는 특성: ${highTraits.map((t) => t.name).join(', ')}\n`;
    }
    if (lowTraits.length > 0) {
      summary += `낮은 수준을 보이는 특성: ${lowTraits.map((t) => t.name).join(', ')}\n`;
    }

    summary += '\n각 특성에 대한 자세한 설명은 아래를 참고해 주세요.';
    return summary;
  } else {
    let summary = 'Here is a summary of your personality profile.\n\n';

    if (highTraits.length > 0) {
      summary += `High traits: ${highTraits.map((t) => t.name).join(', ')}\n`;
    }
    if (lowTraits.length > 0) {
      summary += `Low traits: ${lowTraits.map((t) => t.name).join(', ')}\n`;
    }

    summary += '\nSee below for detailed descriptions of each trait.';
    return summary;
  }
}
