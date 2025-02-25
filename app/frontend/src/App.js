import logo from './logo.svg';
import './App.css';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import SignIn from './pages/SignIn';
import { ThemeProvider, createTheme } from '@mui/material';
import { checkAuth } from './services/api';

const theme = createTheme();

// 인증 상태를 체크하고 필요한 경우 리다이렉션하는 컴포넌트
function AuthCheck({ children }) {
  const navigate = useNavigate();

  // 임시로 인증 체크 비활성화
  /*
  useEffect(() => {
    const checkAuthStatus = async () => {
      const { authenticated, redirect } = await checkAuth();
      if (authenticated && redirect) {
        navigate(redirect);
      }
    };
    checkAuthStatus();
  }, [navigate]);
  */

  return children;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <AuthCheck>
          <Routes>
            <Route path="/" element={<SignIn />} />
            {/* 다른 라우트들도 여기에 추가 */}
          </Routes>
        </AuthCheck>
      </Router>
    </ThemeProvider>
  );
}

export default App;
