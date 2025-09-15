import { useState } from 'react';
import Navbar from './Components/Navbar';
import Footer from './Components/Footer';
import Footer from './Components/Footer';
import SuccessModal from './Components/SuccessModal';

import Home from './Pages/Home';
import About from './Pages/About';
import Faq from './Pages/Faq';
import Privacy from './Pages/Privacy';
import Contact from './Pages/Contact';
import Login from './Pages/Login';
import Auth from './Pages/Auth';
import Dashboard from './Pages/Dashboard';
import CreateReport from './Pages/CreateReport';
import ViewReports from './Pages/ViewReports';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [modalContent, setModalContent] = useState({ title: '', message: '' });

  const navigateTo = (page) => {
    if (['dashboard', 'createReport', 'viewReports'].includes(page) && !isLoggedIn) {
      setCurrentPage('login');
    } else {
      setCurrentPage(page);
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentPage('home');
  };

  const showModal = (title, message) => {
    setModalContent({ title, message });
    setShowSuccessModal(true);
  };

  const closeModal = () => {
    setShowSuccessModal(false);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home': return <Home />;
      case 'about': return <About />;
      case 'faq': return <Faq />;
      case 'privacy': return <Privacy />;
      case 'contact': return <Contact showModal={showModal} />;
      case 'login': return <Login navigateTo={navigateTo} />;
      case 'auth': return <Auth setLoggedIn={setIsLoggedIn} navigateTo={navigateTo} />;
      case 'dashboard': return <Dashboard navigateTo={navigateTo} handleLogout={handleLogout} />;
      case 'createReport': return <CreateReport showModal={showModal} />;
      case 'viewReports': return <ViewReports navigateTo={navigateTo} />;
      default: return <Home />;
    }
  };

  const isPublicPage = ['home', 'about', 'faq', 'privacy', 'contact'].includes(currentPage);
  const isOfficerPortal = ['dashboard', 'createReport', 'viewReports', 'login', 'auth'].includes(currentPage);

  return (
    <>
      {isPublicPage && <Navbar navigateTo={navigateTo} />}
      <div className="pt-16">
        {renderPage()}
      </div>
      {isPublicPage && <Footer navigateTo={navigateTo} />}
      {showSuccessModal && <SuccessModal title={modalContent.title} message={modalContent.message} onClose={closeModal} />}
    </>
  );
}
