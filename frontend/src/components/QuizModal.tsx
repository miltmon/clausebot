import { useState, useCallback, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { X, Lightbulb, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';

interface QuizQuestion {
  id: string;
  q: string;
  a: string[];
  correct: string; // "A", "B", "C", "D"
  category: string;
  explanation: string;
}

interface QuizModalProps {
  isOpen: boolean;
  onClose: () => void;
  category?: string;
}

export const QuizModal = ({ isOpen, onClose, category = "Structural Welding" }: QuizModalProps) => {
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [loading, setLoading] = useState(false);

  const currentQuestion = questions[currentIndex];

  // Fetch quiz questions
  useEffect(() => {
    if (isOpen && questions.length === 0) {
      fetchQuestions();
    }
  }, [isOpen]);

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const res = await fetch(`https://clausebot-api.onrender.com/v1/quiz?category=${encodeURIComponent(category)}&count=5`);
      const data = await res.json();
      
      if (data.items && data.items.length > 0) {
        setQuestions(data.items);
        
        // Track quiz start
        trackEvent('quiz_start', {
          category,
          question_count: data.items.length,
        });
      } else {
        toast.error('No quiz questions available');
        onClose();
      }
    } catch (error) {
      console.error('Quiz fetch error:', error);
      toast.error('Failed to load quiz questions');
      onClose();
    } finally {
      setLoading(false);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen || isAnswered) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // 1-4 for quick selection
      if (['1', '2', '3', '4'].includes(e.key)) {
        const answerIndex = parseInt(e.key) - 1;
        if (currentQuestion && answerIndex < currentQuestion.a.length) {
          handleAnswer(String.fromCharCode(65 + answerIndex)); // Convert to A, B, C, D
        }
      }
      
      // ESC to close
      if (e.key === 'Escape') {
        handleClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isAnswered, currentQuestion]);

  const handleAnswer = useCallback((answer: string) => {
    if (isAnswered || !currentQuestion) return;

    setSelectedAnswer(answer);
    setIsAnswered(true);

    const isCorrect = answer === currentQuestion.correct;
    
    if (isCorrect) {
      setScore(score + 1);
      toast.success('Correct!');
    } else {
      toast.error(`Incorrect. The answer was ${currentQuestion.correct}`);
    }

    // Track answer
    trackEvent('quiz_answer', {
      question_id: currentQuestion.id,
      selected: answer,
      correct: currentQuestion.correct,
      is_correct: isCorrect,
      used_hint: showHint,
    });
  }, [isAnswered, currentQuestion, score, showHint]);

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedAnswer(null);
      setIsAnswered(false);
      setShowHint(false);
    } else {
      // Quiz complete
      trackEvent('quiz_complete', {
        category,
        score,
        total: questions.length,
        percentage: (score / questions.length) * 100,
      });
      
      toast.success(`Quiz complete! Score: ${score}/${questions.length}`);
      onClose();
    }
  };

  const handleClose = useCallback(() => {
    // Track abandonment if quiz not complete
    if (currentIndex < questions.length - 1) {
      trackEvent('quiz_abandon', {
        category,
        questions_answered: currentIndex,
        score,
      });
    }
    
    // Reset state
    setQuestions([]);
    setCurrentIndex(0);
    setSelectedAnswer(null);
    setIsAnswered(false);
    setScore(0);
    setShowHint(false);
    
    onClose();
  }, [onClose, currentIndex, questions.length, category, score]);

  const handleHint = () => {
    setShowHint(true);
    
    trackEvent('quiz_hint_used', {
      question_id: currentQuestion.id,
      category,
    });
  };

  const trackEvent = (eventName: string, params: Record<string, unknown>) => {
    // GA4 tracking
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', eventName, params);
    }
  };

  if (!currentQuestion && !loading) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent 
        className="max-w-2xl" 
        aria-labelledby="quiz-title"
        aria-describedby="quiz-description"
      >
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle id="quiz-title">ClauseBot Quiz</DialogTitle>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleClose();
              }}
              className="rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              aria-label="Close ClauseBot quiz modal"
              type="button"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </button>
          </div>
          <div id="quiz-description" className="flex items-center justify-between text-sm text-muted-foreground">
            <Badge variant="outline" role="status" aria-live="polite">
              Question {currentIndex + 1} of {questions.length}
            </Badge>
            <span role="status" aria-live="polite" aria-label={`Current score: ${score} out of ${currentIndex + (isAnswered ? 1 : 0)}`}>
              Score: {score}/{currentIndex + (isAnswered ? 1 : 0)}
            </span>
          </div>
        </DialogHeader>

        {loading ? (
          <div className="py-12 text-center" role="status" aria-live="polite">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary" aria-hidden="true"></div>
            <p className="mt-4 text-muted-foreground">Loading quiz questions...</p>
          </div>
        ) : (
          <div className="space-y-6 py-4">
            {/* Question */}
            <h2 className="text-lg font-medium" id={`question-${currentQuestion.id}`}>
              {currentQuestion.q}
            </h2>

            {/* Answer Options */}
            <fieldset className="space-y-3">
              <legend className="sr-only">
                Select your answer for question {currentIndex + 1}
              </legend>
              {currentQuestion.a.map((option, index) => {
                const letter = String.fromCharCode(65 + index); // A, B, C, D
                const isSelected = selectedAnswer === letter;
                const isCorrect = letter === currentQuestion.correct;
                const showCorrect = isAnswered && isCorrect;
                const showIncorrect = isAnswered && isSelected && !isCorrect;

                return (
                  <button
                    key={letter}
                    onClick={() => handleAnswer(letter)}
                    disabled={isAnswered}
                    type="button"
                    role="radio"
                    aria-checked={isSelected}
                    aria-labelledby={`answer-${letter}-${currentQuestion.id}`}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      showCorrect
                        ? 'border-green-500 bg-green-50'
                        : showIncorrect
                        ? 'border-red-500 bg-red-50'
                        : isSelected
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    } ${isAnswered ? 'cursor-default' : 'cursor-pointer'}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge 
                          variant={isAnswered ? (isCorrect ? 'default' : 'outline') : 'secondary'}
                          aria-hidden="true"
                        >
                          {letter}
                        </Badge>
                        <span id={`answer-${letter}-${currentQuestion.id}`}>{option}</span>
                      </div>
                      {showCorrect && <CheckCircle className="h-5 w-5 text-green-600" aria-label="Correct answer" />}
                      {showIncorrect && <XCircle className="h-5 w-5 text-red-600" aria-label="Incorrect answer" />}
                    </div>
                  </button>
                );
              })}
            </fieldset>

            {/* Hint System */}
            {!isAnswered && !showHint && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleHint} 
                className="gap-2"
                aria-label="Show hint for current question"
                type="button"
              >
                <Lightbulb className="h-4 w-4" aria-hidden="true" />
                Show Hint
              </Button>
            )}

            {showHint && !isAnswered && (
              <div 
                className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm"
                role="region"
                aria-label="Question hint"
              >
                <div className="font-medium text-blue-900 mb-1">Hint:</div>
                <div className="text-blue-800">
                  Think about the category: {currentQuestion.category || 'General'}
                </div>
              </div>
            )}

            {/* Explanation (after answer) */}
            {isAnswered && currentQuestion.explanation && (
              <div 
                className="p-4 bg-muted rounded-lg text-sm"
                role="region"
                aria-live="polite"
                aria-label="Answer explanation"
              >
                <div className="font-medium mb-1">Explanation:</div>
                <div>{currentQuestion.explanation}</div>
              </div>
            )}

            {/* Navigation */}
            {isAnswered && (
              <div className="flex justify-end">
                <Button 
                  onClick={handleNext}
                  type="button"
                  aria-label={currentIndex < questions.length - 1 ? 'Continue to next question' : 'Finish quiz and view results'}
                >
                  {currentIndex < questions.length - 1 ? 'Next Question' : 'Finish Quiz'}
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Footer Hint */}
        <div className="text-xs text-center text-muted-foreground border-t pt-4">
          Press 1-4 for quick selection • ESC to close
        </div>
      </DialogContent>
    </Dialog>
  );
};
