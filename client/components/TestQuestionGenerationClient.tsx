'use client';

import { QuestionGeneration } from '@/components/QuestionGeneration';

export default function TestQuestionGenerationClient() {
  return (
    <QuestionGeneration
      documentName="Sample Document.pdf"
      isGenerating={false}
      onGenerate={(data) => {
        console.log('✅ Validation passed! Generated questions with data:', data);
        alert(`Success! Generated ${data.numberOfQuestions} ${data.questionType} questions at ${data.bloomLevel} level with ${data.difficulty} difficulty.`);
      }}
    />
  );
}
