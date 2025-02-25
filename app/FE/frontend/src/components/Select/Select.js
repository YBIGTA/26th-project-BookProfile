import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { BookCard } from "../BookCard/BookCard";
import "./Select.css";

// 책 목록을 2개씩 5줄로 재배열
const bookRows = [
  [
    {
      id: 1,
      title: "The Catcher in the Rye",
      author: "J.D. Salinger",
      imageSrc: "/book1.jpg"
    },
    {
      id: 2,
      title: "To Kill a Mockingbird",
      author: "Harper Lee",
      imageSrc: "/book2.jpg"
    }
  ],
  [
    {
      id: 3,
      title: "1984",
      author: "George Orwell",
      imageSrc: "/book3.jpg"
    },
    {
      id: 4,
      title: "Pride and Prejudice",
      author: "Jane Austen",
      imageSrc: "/book4.jpg"
    }
  ],
  [
    {
      id: 5,
      title: "The Great Gatsby",
      author: "F. Scott Fitzgerald",
      imageSrc: "/book5.jpg"
    },
    {
      id: 6,
      title: "One Hundred Years of Solitude",
      author: "Gabriel García Márquez",
      imageSrc: "/book6.jpg"
    }
  ],
  [
    {
      id: 7,
      title: "Brave New World",
      author: "Aldous Huxley",
      imageSrc: "/book7.jpg"
    },
    {
      id: 8,
      title: "The Lord of the Rings",
      author: "J.R.R. Tolkien",
      imageSrc: "/book8.jpg"
    }
  ],
  [
    {
      id: 9,
      title: "Crime and Punishment",
      author: "Fyodor Dostoevsky",
      imageSrc: "/book9.jpg"
    },
    {
      id: 10,
      title: "The Picture of Dorian Gray",
      author: "Oscar Wilde",
      imageSrc: "/book10.jpg"
    }
  ]
];

export const Select = () => {
  const navigate = useNavigate();
  const [ratings, setRatings] = useState({});

  const handleRatingChange = (bookId, rating) => {
    setRatings(prev => ({
      ...prev,
      [bookId]: rating
    }));
  };

  const handleFinish = () => {
    // 여기서 ratings 데이터를 처리할 수 있습니다
    console.log('Book ratings:', ratings);
    // MainPage로 이동
    navigate('/bookshelf');
  };

  const allBooksRated = () => {
    const ratedBooks = Object.keys(ratings).length;
    const totalBooks = bookRows.flat().length;
    return ratedBooks === totalBooks;
  };

  return (
    <div className="select-page">
      <h1 className="select-title">BOOKSELF</h1>
      <p className="select-subtitle">Please rate the following books</p>
      
      <div className="books-container">
        {bookRows.map((row, rowIndex) => (
          <div key={rowIndex} className="book-row">
            {row.map((book) => (
              <BookCard
                key={book.id}
                title={book.title}
                author={book.author}
                imageSrc={book.imageSrc}
                onRatingChange={(rating) => handleRatingChange(book.id, rating)}
              />
            ))}
          </div>
        ))}
      </div>

      <button 
        className={`finish-button ${allBooksRated() ? 'active' : 'disabled'}`}
        onClick={handleFinish}
        disabled={!allBooksRated()}
      >
        Finish
      </button>
    </div>
  );
};
