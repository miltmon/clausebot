import React, { useState, useEffect } from "react";

type QuizItem = {
  id: string;
  question: string;
  options: string[];
  correct_answer: string; // "A", "B", "C", "D"
  hint?: string;
  clause_ref?: string;
  explanation?: string;
  category?: string;
};

type QuizResponse = {
  count: number;
  category: string;
  source: string;
  items: QuizItem[];
};

interface QuizModalProps {
  open: boolean;
  onClose: () => void;
}

export const QuizModal = ({ open, onClose }: QuizModalProps) => {
  const [questions, setQuestions] = useState<QuizItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(false);

  const currentQuestion = questions[currentIndex];

  // Fetch quiz questions when modal opens
  useEffect(() => {
    if (open && questions.length === 0) {
      fetchQuestions();
    }
  }, [open, questions.length]);

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const response = await fetch("https://clausebot-api.onrender.com/v1/quiz?count=5");
      const data: QuizResponse = await response.json();
      
      if (data.items && data.items.length > 0) {
        setQuestions(data.items);
        
        // Track quiz start in GA4
        if (typeof window !== 'undefined' && window.gtag) {
          window.gtag('event', 'quiz_start', {
            category: data.category,
            question_count: data.items.length,
          });
        }
      }
    } catch (error) {
      console.error('Quiz fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (answer: string) => {
    if (isAnswered) return;

    setSelectedAnswer(answer);
    setIsAnswered(true);

    const isCorrect = answer === currentQuestion.correct_answer;
    if (isCorrect) {
      setScore(score + 1);
    }

    // Track answer in GA4
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'quiz_answer', {
        question_id: currentQuestion.id,
        selected: answer,
        correct: currentQuestion.correct_answer,
        is_correct: isCorrect,
      });
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedAnswer(null);
      setIsAnswered(false);
    } else {
      // Quiz complete
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'quiz_complete', {
          score,
          total: questions.length,
          percentage: Math.round((score / questions.length) * 100),
        });
      }
      handleClose();
    }
  };

  const handleClose = () => {
    // Reset state
    setQuestions([]);
    setCurrentIndex(0);
    setSelectedAnswer(null);
    setIsAnswered(false);
    setScore(0);
    setLoading(false);
    onClose();
  };

  if (!open) return null;

  if (loading) {
    return (
      <div 
        role="dialog" 
        aria-modal="true" 
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      >
        <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p>Loading quiz questions...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div 
        role="dialog" 
        aria-modal="true" 
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      >
        <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
          <button 
            aria-label="Close quiz" 
            onClick={handleClose}
            className="float-right text-gray-500 hover:text-gray-700 text-xl font-bold"
          >
            ×
          </button>
          <p className="text-center text-gray-600">No questions available.</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      role="dialog" 
      aria-modal="true" 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-bold">ClauseBot Quiz</h2>
            <p className="text-sm text-gray-600">
              Question {currentIndex + 1} of {questions.length} | Score: {score}/{currentIndex + (isAnswered ? 1 : 0)}
            </p>
          </div>
          <button 
            aria-label="Close quiz" 
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Question */}
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-4">{currentQuestion.question}</h3>
          
          {/* Answer Options */}
          <div className="space-y-3">
            {currentQuestion.options.map((option, index) => {
              const letter = String.fromCharCode(65 + index); // A, B, C, D
              const isSelected = selectedAnswer === letter;
              const isCorrect = letter === currentQuestion.correct_answer;
              const showCorrect = isAnswered && isCorrect;
              const showIncorrect = isAnswered && isSelected && !isCorrect;

              return (
                <button
                  key={letter}
                  onClick={() => handleAnswer(letter)}
                  disabled={isAnswered}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    showCorrect
                      ? 'border-green-500 bg-green-50'
                      : showIncorrect
                      ? 'border-red-500 bg-red-50'
                      : isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  } ${isAnswered ? 'cursor-default' : 'cursor-pointer'}`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                      showCorrect ? 'bg-green-600 text-white' :
                      showIncorrect ? 'bg-red-600 text-white' :
                      isSelected ? 'bg-blue-600 text-white' :
                      'bg-gray-200 text-gray-700'
                    }`}>
                      {letter}
                    </span>
                    <span>{option}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Explanation (after answer) */}
        {isAnswered && currentQuestion.explanation && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Explanation:</h4>
            <p className="text-sm text-gray-700">{currentQuestion.explanation}</p>
            {currentQuestion.clause_ref && (
              <p className="text-xs text-gray-500 mt-2">
                Reference: {currentQuestion.clause_ref}
              </p>
            )}
          </div>
        )}

        {/* Navigation */}
        {isAnswered && (
          <div className="flex justify-end">
            <button
              onClick={handleNext}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {currentIndex < questions.length - 1 ? 'Next Question' : 'Finish Quiz'}
            </button>
          </div>
        )}

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500 text-center">
          Press A-D for quick selection • ESC to close
        </div>
      </div>
    </div>
  );
};
