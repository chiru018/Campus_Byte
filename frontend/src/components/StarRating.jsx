import React, { useState } from 'react';
import './StarRating.scss';

export const StarRating = ({
  rating = 0,
  maxStars = 5,
  onChange = null,
  readonly = false,
  size = 'md',
  showValue = false,
}) => {
  const [hoverRating, setHoverRating] = useState(0);

  const displayRating = hoverRating || rating;

  const handleClick = (value) => {
    if (!readonly && onChange) {
      onChange(value);
    }
  };

  const handleMouseEnter = (value) => {
    if (!readonly) {
      setHoverRating(value);
    }
  };

  const handleMouseLeave = () => {
    if (!readonly) {
      setHoverRating(0);
    }
  };

  return (
    <div
      className={`star-rating star-rating--${size} ${readonly ? 'star-rating--readonly' : 'star-rating--interactive'}`}
      onMouseLeave={handleMouseLeave}
      role={readonly ? 'img' : 'radiogroup'}
      aria-label={`Rating: ${rating} out of ${maxStars} stars`}
    >
      {Array.from({ length: maxStars }, (_, index) => {
        const starValue = index + 1;
        const isFilled = starValue <= Math.round(displayRating);

        return readonly ? (
          <span
            key={starValue}
            className={`star-rating__star ${isFilled ? 'star-rating__star--filled' : 'star-rating__star--empty'}`}
            aria-hidden="true"
          >
            ★
          </span>
        ) : (
          <button
            key={starValue}
            type="button"
            className={`star-rating__star-btn ${isFilled ? 'star-rating__star-btn--filled' : 'star-rating__star-btn--empty'}`}
            onClick={() => handleClick(starValue)}
            onMouseEnter={() => handleMouseEnter(starValue)}
            aria-label={`${starValue} star${starValue > 1 ? 's' : ''}`}
          >
            ★
          </button>
        );
      })}

      {showValue && (
        <span className="star-rating__value">
          {Number(rating).toFixed(1)}
        </span>
      )}
    </div>
  );
};

export default StarRating;

