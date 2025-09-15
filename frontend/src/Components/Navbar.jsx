import { useState } from 'react';

// SVG Icons
const ShieldCheckIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>`;
const MenuIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16m-7 6h7" /></svg>`;
const XIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>`;

export default function Navbar({ navigateTo }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white/80 backdrop-blur-md shadow-sm fixed w-full z-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <button onClick={() => navigateTo('home')} className="flex-shrink-0 flex items-center gap-2 text-xl font-bold text-blue-600">
              <span dangerouslySetInnerHTML={{ __html: ShieldCheckIcon }} />
              <span>SafeIMEI</span>
            </button>
          </div>
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <button onClick={() => navigateTo('home')} className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">Home</button>
              <button onClick={() => navigateTo('about')} className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">About</button>
              <button onClick={() => navigateTo('faq')} className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">FAQ</button>
              <button onClick={() => navigateTo('contact')} className="text-gray-600 hover:bg-gray-100 hover:hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">Contact</button>
              <button onClick={() => navigateTo('privacy')} className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">Privacy</button>
              <button onClick={() => navigateTo('login')} className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-transform transform hover:scale-105">Officer Portal</button>
            </div>
          </div>
          <div className="-mr-2 flex md:hidden">
            <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="bg-gray-100 inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-900 hover:bg-gray-200">
              <span dangerouslySetInnerHTML={{ __html: isMobileMenuOpen ? XIcon : MenuIcon }} />
            </button>
          </div>
        </div>
      </div>
      <div className={`md:hidden ${isMobileMenuOpen ? 'block' : 'hidden'}`}>
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <button onClick={() => navigateTo('home')} className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 block px-3 py-2 rounded-md text-base font-medium w-full text-left">Home</button>
          <button onClick={() => navigateTo('about')} className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 block px-3 py-2 rounded-md text-base font-medium w-full text-left">About</button>
          <button onClick={() => navigateTo('faq')} className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 block px-3 py-2 rounded-md text-base font-medium w-full text-left">FAQ</button>
          <button onClick={() => navigateTo('contact')} className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 block px-3 py-2 rounded-md text-base font-medium w-full text-left">Contact</button>
          <button onClick={() => navigateTo('privacy')} className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 block px-3 py-2 rounded-md text-base font-medium w-full text-left">Privacy</button>
          <button onClick={() => navigateTo('login')} className="bg-blue-600 text-white mt-2 block px-3 py-2 rounded-md text-base font-medium w-full text-left hover:bg-blue-700">Officer Portal</button>
        </div>
      </div>
    </nav>
  );
}