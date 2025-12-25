/**
 * Internationalization (i18n) translations for Korean and English.
 */

export type Language = 'en' | 'kr';

export interface Translations {
  // Common
  common: {
    loading: string;
    error: string;
    returnToHub: string;
    continue: string;
    start: string;
    submit: string;
    done: string;
    next: string;
    back: string;
    completed: string;
  };

  // Landing page
  landing: {
    title: string;
    subtitle: string;
    ageLabel: string;
    agePlaceholder: string;
    genderLabel: string;
    genderOptions: {
      preferNot: string;
      male: string;
      female: string;
      nonBinary: string;
      other: string;
    };
    startButton: string;
    startingButton: string;
    assessmentInfo: string;
    assessmentTypes: string[];
    randomOrderNote: string;
    selectLanguage: string;
  };

  // Assessment hub
  hub: {
    title: string;
    participantLabel: string;
    completedLabel: string;
    conditionNames: {
      survey: string;
      dose: string;
    };
    conditionDescriptions: {
      survey: string;
      dose: string;
    };
    allComplete: {
      title: string;
      message: string;
      viewResults: string;
    };
  };

  // Survey page
  survey: {
    title: string;
    progress: string;
    instructions: string;
    submitButton: string;
    answerRemaining: string;
  };

  // DOSE chatbot
  dose: {
    title: string;
    questionsLabel: string;
    seThreshold: string;
    welcomeMessage: string;
    itemPrompt: string;
    completeMessage: string;
    assessingLabel: string;
    continueButton: string;
    nextItemIntro: string;
    itemReductionMessage: string;
    questionNumber: string;
  };

  // Likert scale
  likert: {
    labels: string[];
    instruction: string;
  };

  // Results page
  results: {
    title: string;
    participantLabel: string;
    assessmentsComplete: string;
    traitComparison: string;
    efficiencyMetrics: string;
    items: string;
    duration: string;
    reduction: string;
    accuracyTitle: string;
    correlation: string;
    mae: string;
    traitDifferences: string;
    insightsTitle: string;
    insightsDescription: string;
    strongCorrelation: string;
    doseEfficiency: string;
    backButton: string;
    continueToFeedback: string;
    personalityProfileTitle: string;
    personalityProfileIntro: string;
    scoreLevelHigh: string;
    scoreLevelModerate: string;
    scoreLevelLow: string;
  };

  // Satisfaction survey
  satisfaction: {
    title: string;
    intro: string;
    overallRatingLabel: string;
    overallRatingDescription: string;
    preferredMethodLabel: string;
    preferredMethodDescription: string;
    preferredSurvey: string;
    preferredDose: string;
    doseEaseLabel: string;
    doseEaseDescription: string;
    wouldRecommendLabel: string;
    wouldRecommendDescription: string;
    openFeedbackLabel: string;
    openFeedbackPlaceholder: string;
    submitButton: string;
    submitting: string;
    thankYouTitle: string;
    thankYouMessage: string;
    returnHome: string;
    alreadyCompleted: string;
    starLabels: string[];
    likertLabels: string[];
  };

  // Trait names
  traits: {
    extraversion: string;
    agreeableness: string;
    conscientiousness: string;
    neuroticism: string;
    openness: string;
    honesty_humility: string;
  };
}

export const translations: Record<Language, Translations> = {
  en: {
    common: {
      loading: 'Loading...',
      error: 'Error',
      returnToHub: 'Return to Hub',
      continue: 'Continue',
      start: 'Start',
      submit: 'Submit',
      done: 'Done',
      next: 'Next',
      back: 'Back',
      completed: 'Completed',
    },

    landing: {
      title: 'Personality Assessment',
      subtitle: 'Compare different methods of personality assessment through chatbot interactions.',
      ageLabel: 'Age (optional)',
      agePlaceholder: 'Enter your age',
      genderLabel: 'Gender (optional)',
      genderOptions: {
        preferNot: 'Prefer not to say',
        male: 'Male',
        female: 'Female',
        nonBinary: 'Non-binary',
        other: 'Other',
      },
      startButton: 'Start Assessment',
      startingButton: 'Starting...',
      assessmentInfo: 'You will complete 2 different types of assessments:',
      assessmentTypes: [
        'Traditional Survey (24 questions)',
        'Adaptive (DOSE) Chatbot (fewer questions)',
      ],
      randomOrderNote: 'The order will be randomly assigned.',
      selectLanguage: 'Select Language',
    },

    hub: {
      title: 'Assessment Hub',
      participantLabel: 'Participant',
      completedLabel: 'Completed',
      conditionNames: {
        survey: 'Traditional Survey',
        dose: 'Adaptive (DOSE) Chatbot',
      },
      conditionDescriptions: {
        survey: 'Answer all 24 questions in a traditional form format.',
        dose: 'An intelligent chatbot that adapts questions based on your responses. Uses fewer questions to assess your personality.',
      },
      allComplete: {
        title: 'All Assessments Complete!',
        message: 'Thank you for participating in this research study.',
        viewResults: 'View Results',
      },
    },

    survey: {
      title: 'Traditional Survey',
      progress: '{answered} of {total} questions answered',
      instructions: 'Hello! Please read each statement below and think about how well it describes you in general. Select the response that best fits you. There are no right or wrong answers, so please respond honestly and comfortably.',
      submitButton: 'Submit Survey',
      answerRemaining: 'Please answer the remaining {remaining} questions',
    },

    dose: {
      title: 'Adaptive (DOSE) Chatbot',
      questionsLabel: 'Questions',
      seThreshold: 'SE Threshold: 0.3',
      welcomeMessage: "Hello! Nice to meet you. I'm here to help understand your personality traits through a few questions. Based on your responses, I'll select the most relevant questions so we can get accurate results with fewer items. Please feel free to answer honestly!",
      itemPrompt: 'Please select how well this statement describes you in general.',
      completeMessage: "Great job! I've gathered enough information to understand your personality traits. Thank you so much for your participation!",
      assessingLabel: 'Currently assessing',
      continueButton: 'Continue to Next Assessment',
      nextItemIntro: "Thank you for your response! Here's the next statement:",
      itemReductionMessage: 'I used only {count} questions instead of the full 24!',
      questionNumber: 'Question {number}',
    },

    likert: {
      labels: [
        'Very Inaccurate',
        'Inaccurate',
        'Somewhat Inaccurate',
        'Neutral',
        'Somewhat Accurate',
        'Accurate',
        'Very Accurate',
      ],
      instruction: 'Select how accurately this describes you',
    },

    results: {
      title: 'Assessment Results',
      participantLabel: 'Participant',
      assessmentsComplete: 'Assessments Complete',
      traitComparison: 'Trait Scores Comparison',
      efficiencyMetrics: 'Efficiency Metrics',
      items: 'Items',
      duration: 'Duration',
      reduction: 'Reduction',
      accuracyTitle: 'DOSE Accuracy vs. Traditional Survey (Baseline)',
      correlation: 'Correlation (r)',
      mae: 'Mean Absolute Error',
      traitDifferences: 'Trait Differences',
      insightsTitle: 'Research Insights',
      insightsDescription: 'This study compares the Traditional Survey with the DOSE Adaptive Chatbot using the Mini-IPIP6 scale (24 items, 6 traits from the HEXACO model).',
      strongCorrelation: 'Strong correlation (r >= 0.9) found, indicating the DOSE chatbot can accurately replicate traditional survey results.',
      doseEfficiency: 'DOSE achieved >=50% item reduction while maintaining accuracy, demonstrating the efficiency of adaptive testing.',
      backButton: 'Back to Assessment Hub',
      continueToFeedback: 'Continue to Feedback Survey',
      personalityProfileTitle: 'Your Personality Profile',
      personalityProfileIntro: 'Based on your responses, here is an interpretation of your personality traits. Remember, there are no "good" or "bad" traits - each represents different strengths and tendencies.',
      scoreLevelHigh: 'High',
      scoreLevelModerate: 'Moderate',
      scoreLevelLow: 'Low',
    },

    satisfaction: {
      title: 'Feedback Survey',
      intro: 'Thank you for completing the assessments! Please take a moment to share your experience. Your feedback helps us improve our research.',
      overallRatingLabel: 'Overall Experience',
      overallRatingDescription: 'How would you rate your overall experience with this study?',
      preferredMethodLabel: 'Preferred Assessment Method',
      preferredMethodDescription: 'Which assessment method did you prefer?',
      preferredSurvey: 'Traditional Survey (24 questions)',
      preferredDose: 'Adaptive Chatbot (fewer questions)',
      doseEaseLabel: 'Chatbot Ease of Use',
      doseEaseDescription: 'How easy was it to use the adaptive (DOSE) chatbot?',
      wouldRecommendLabel: 'Recommendation',
      wouldRecommendDescription: 'Would you recommend this type of assessment to others?',
      openFeedbackLabel: 'Additional Comments (Optional)',
      openFeedbackPlaceholder: 'Please share any additional thoughts, suggestions, or feedback about your experience...',
      submitButton: 'Submit Feedback',
      submitting: 'Submitting...',
      thankYouTitle: 'Thank You!',
      thankYouMessage: 'Your feedback has been recorded. We appreciate your participation in this research study.',
      returnHome: 'Return to Home',
      alreadyCompleted: 'You have already completed the feedback survey. Thank you for your participation!',
      starLabels: ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'],
      likertLabels: ['Strongly Disagree', 'Disagree', 'Somewhat Disagree', 'Neutral', 'Somewhat Agree', 'Agree', 'Strongly Agree'],
    },

    traits: {
      extraversion: 'Extraversion',
      agreeableness: 'Agreeableness',
      conscientiousness: 'Conscientiousness',
      neuroticism: 'Neuroticism',
      openness: 'Openness',
      honesty_humility: 'Honesty-Humility',
    },
  },

  kr: {
    common: {
      loading: '잠시만 기다려 주세요...',
      error: '오류가 발생했습니다',
      returnToHub: '검사 허브로 돌아가기',
      continue: '계속하기',
      start: '시작하기',
      submit: '제출하기',
      done: '완료',
      next: '다음',
      back: '이전으로',
      completed: '완료됨',
    },

    landing: {
      title: '성격 검사',
      subtitle: '본 연구는 챗봇을 활용한 성격 평가 방법을 비교하는 연구입니다. 참여해 주셔서 감사합니다.',
      ageLabel: '나이 (선택사항)',
      agePlaceholder: '나이를 입력해 주세요',
      genderLabel: '성별 (선택사항)',
      genderOptions: {
        preferNot: '응답하지 않음',
        male: '남성',
        female: '여성',
        nonBinary: '논바이너리',
        other: '기타',
      },
      startButton: '검사 시작하기',
      startingButton: '시작하는 중...',
      assessmentInfo: '총 2가지 유형의 검사에 참여하시게 됩니다:',
      assessmentTypes: [
        '전통적 설문조사 (24개 문항)',
        '적응형 (DOSE) 챗봇 (더 적은 문항)',
      ],
      randomOrderNote: '검사 순서는 무작위로 배정됩니다.',
      selectLanguage: '언어 선택',
    },

    hub: {
      title: '검사 허브',
      participantLabel: '참가자 번호',
      completedLabel: '완료',
      conditionNames: {
        survey: '전통적 설문조사',
        dose: '적응형 (DOSE) 챗봇',
      },
      conditionDescriptions: {
        survey: '전통적인 설문 형식으로 24개의 모든 문항에 답변해 주시면 됩니다.',
        dose: '귀하의 응답에 따라 적절한 문항을 선별하는 지능형 챗봇입니다. 더 적은 문항으로도 정확하게 성격을 평가할 수 있습니다.',
      },
      allComplete: {
        title: '모든 검사가 완료되었습니다!',
        message: '소중한 시간 내어 연구에 참여해 주셔서 진심으로 감사드립니다.',
        viewResults: '결과 확인하기',
      },
    },

    survey: {
      title: '전통적 설문조사',
      progress: '{total}개 문항 중 {answered}개 응답 완료',
      instructions: '안녕하세요! 아래 각 문장이 평소 본인의 모습을 얼마나 잘 나타내는지 생각해 보시고, 가장 적절한 응답을 선택해 주세요. 정답은 없으니 편하게 솔직하게 답변해 주시면 됩니다.',
      submitButton: '설문 제출하기',
      answerRemaining: '나머지 {remaining}개 문항에 답변해 주세요',
    },

    dose: {
      title: '적응형 (DOSE) 챗봇',
      questionsLabel: '문항 수',
      seThreshold: 'SE 임계값: 0.3',
      welcomeMessage: '안녕하세요! 반갑습니다. 저는 귀하의 성격 특성을 파악하기 위해 몇 가지 질문을 드릴 예정입니다. 응답해 주시는 내용을 바탕으로 다음 질문을 선별하여, 적은 문항으로도 정확한 결과를 얻을 수 있도록 도와드리겠습니다. 편안하게 답변해 주세요!',
      itemPrompt: '아래 문장이 평소 본인의 모습을 얼마나 잘 나타내는지 선택해 주세요.',
      completeMessage: '수고하셨습니다! 귀하의 성격 특성을 파악하기에 충분한 정보가 수집되었습니다. 참여해 주셔서 진심으로 감사드립니다.',
      assessingLabel: '현재 평가 중인 특성',
      continueButton: '다음 검사로 이동하기',
      nextItemIntro: '응답해 주셔서 감사합니다! 다음 문항입니다:',
      itemReductionMessage: '전체 24개 문항 대신 {count}개의 문항만으로 검사를 완료하였습니다!',
      questionNumber: '{number}번 문항',
    },

    likert: {
      labels: [
        '매우 부정확',
        '부정확',
        '약간 부정확',
        '보통',
        '약간 정확',
        '정확',
        '매우 정확',
      ],
      instruction: '이 문장이 본인을 얼마나 정확하게 설명하는지 선택하세요',
    },

    results: {
      title: '검사 결과',
      participantLabel: '참가자 번호',
      assessmentsComplete: '검사 완료',
      traitComparison: '성격 특성 점수 비교',
      efficiencyMetrics: '효율성 지표',
      items: '문항 수',
      duration: '소요 시간',
      reduction: '문항 감소율',
      accuracyTitle: 'DOSE 정확도 vs. 전통적 설문조사 (기준)',
      correlation: '상관계수 (r)',
      mae: '평균 절대 오차',
      traitDifferences: '특성별 차이',
      insightsTitle: '연구 결과 요약',
      insightsDescription: '본 연구는 Mini-IPIP6 척도(24개 문항, HEXACO 모델의 6가지 성격 특성)를 사용하여 전통적 설문조사와 DOSE 적응형 챗봇의 결과를 비교하였습니다.',
      strongCorrelation: '강한 상관관계(r >= 0.9)가 확인되어, DOSE 챗봇이 전통적 설문조사 결과를 정확하게 재현할 수 있음을 보여줍니다.',
      doseEfficiency: 'DOSE는 정확도를 유지하면서 50% 이상의 문항 감소를 달성하여, 적응형 검사의 우수한 효율성을 입증하였습니다.',
      backButton: '검사 허브로 돌아가기',
      continueToFeedback: '피드백 설문으로 이동하기',
      personalityProfileTitle: '귀하의 성격 프로필',
      personalityProfileIntro: '응답을 바탕으로 귀하의 성격 특성을 해석해 드립니다. "좋은" 특성이나 "나쁜" 특성은 없으며, 각 특성은 서로 다른 강점과 성향을 나타냅니다.',
      scoreLevelHigh: '높음',
      scoreLevelModerate: '보통',
      scoreLevelLow: '낮음',
    },

    satisfaction: {
      title: '피드백 설문',
      intro: '검사를 완료해 주셔서 감사합니다! 잠시 시간을 내어 경험을 공유해 주세요. 귀하의 피드백은 연구 개선에 큰 도움이 됩니다.',
      overallRatingLabel: '전반적인 경험',
      overallRatingDescription: '본 연구에 참여한 전반적인 경험은 어떠셨나요?',
      preferredMethodLabel: '선호하는 검사 방식',
      preferredMethodDescription: '어떤 검사 방식이 더 좋으셨나요?',
      preferredSurvey: '전통적 설문조사 (24개 문항)',
      preferredDose: '적응형 챗봇 (더 적은 문항)',
      doseEaseLabel: '챗봇 사용 편의성',
      doseEaseDescription: '적응형 (DOSE) 챗봇은 사용하기 얼마나 편하셨나요?',
      wouldRecommendLabel: '추천 의향',
      wouldRecommendDescription: '이러한 유형의 검사를 다른 사람에게 추천하시겠습니까?',
      openFeedbackLabel: '추가 의견 (선택사항)',
      openFeedbackPlaceholder: '경험에 대한 추가적인 생각, 제안, 또는 피드백이 있으시면 자유롭게 작성해 주세요...',
      submitButton: '피드백 제출하기',
      submitting: '제출 중...',
      thankYouTitle: '감사합니다!',
      thankYouMessage: '피드백이 기록되었습니다. 연구에 참여해 주셔서 진심으로 감사드립니다.',
      returnHome: '홈으로 돌아가기',
      alreadyCompleted: '이미 피드백 설문을 완료하셨습니다. 참여해 주셔서 감사합니다!',
      starLabels: ['매우 불만족', '불만족', '보통', '만족', '매우 만족'],
      likertLabels: ['매우 그렇지 않다', '그렇지 않다', '약간 그렇지 않다', '보통이다', '약간 그렇다', '그렇다', '매우 그렇다'],
    },

    traits: {
      extraversion: '외향성',
      agreeableness: '우호성',
      conscientiousness: '성실성',
      neuroticism: '신경증',
      openness: '개방성',
      honesty_humility: '정직-겸손',
    },
  },
};

// Mini-IPIP6 item translations
export const itemTranslations: Record<Language, Record<number, string>> = {
  en: {
    1: "Am the life of the party.",
    2: "Sympathize with others' feelings.",
    3: "Get chores done right away.",
    4: "Have frequent mood swings.",
    5: "Have a vivid imagination.",
    6: "Feel entitled to more of everything.",
    7: "Don't talk a lot.",
    8: "Am not interested in other people's problems.",
    9: "Have difficulty understanding abstract ideas.",
    10: "Like order.",
    11: "Make a mess of things.",
    12: "Deserve more things in life.",
    13: "Do not have a good imagination.",
    14: "Feel others' emotions.",
    15: "Am relaxed most of the time.",
    16: "Get upset easily.",
    17: "Seldom feel blue.",
    18: "Would like to be seen driving around in a very expensive car.",
    19: "Keep in the background.",
    20: "Am not really interested in others.",
    21: "Am not interested in abstract ideas.",
    22: "Often forget to put things back in their proper place.",
    23: "Talk to a lot of different people at parties.",
    24: "Would get a lot of pleasure from owning expensive luxury goods.",
  },
  kr: {
    1: "나는 파티의 분위기 메이커이다.",
    2: "나는 다른 사람들의 감정에 공감한다.",
    3: "나는 집안일을 바로바로 처리한다.",
    4: "나는 기분 변화가 자주 있다.",
    5: "나는 생생한 상상력을 가지고 있다.",
    6: "나는 모든 것에서 더 많은 것을 받을 자격이 있다고 느낀다.",
    7: "나는 말을 많이 하지 않는다.",
    8: "나는 다른 사람들의 문제에 관심이 없다.",
    9: "나는 추상적인 아이디어를 이해하는 데 어려움이 있다.",
    10: "나는 질서를 좋아한다.",
    11: "나는 일을 엉망으로 만든다.",
    12: "나는 인생에서 더 많은 것을 받을 자격이 있다.",
    13: "나는 상상력이 좋지 않다.",
    14: "나는 다른 사람들의 감정을 느낀다.",
    15: "나는 대부분의 시간 동안 편안하다.",
    16: "나는 쉽게 화가 난다.",
    17: "나는 거의 우울하지 않다.",
    18: "나는 매우 비싼 차를 운전하는 모습을 보여주고 싶다.",
    19: "나는 뒤에서 조용히 있는 편이다.",
    20: "나는 다른 사람들에게 별로 관심이 없다.",
    21: "나는 추상적인 아이디어에 관심이 없다.",
    22: "나는 물건을 제자리에 돌려놓는 것을 자주 잊어버린다.",
    23: "나는 파티에서 다양한 사람들과 대화한다.",
    24: "나는 비싼 명품을 소유하는 것에서 큰 즐거움을 얻을 것이다.",
  },
};

/**
 * Get translation for a specific key path
 */
export function t(translations: Translations, path: string): string {
  const keys = path.split('.');
  let result: unknown = translations;

  for (const key of keys) {
    if (result && typeof result === 'object' && key in result) {
      result = (result as Record<string, unknown>)[key];
    } else {
      return path; // Return path if not found
    }
  }

  return typeof result === 'string' ? result : path;
}

/**
 * Get item text in specified language
 */
export function getItemText(itemNumber: number, lang: Language): string {
  return itemTranslations[lang][itemNumber] || itemTranslations.en[itemNumber];
}

/**
 * Get trait name in specified language
 */
export function getTraitName(trait: string, lang: Language): string {
  const traitKey = trait as keyof Translations['traits'];
  return translations[lang].traits[traitKey] || trait;
}
