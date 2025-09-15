export default function Footer({ navigateTo }) {
    return (
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex justify-center space-x-6 md:order-2">
              <button onClick={() => navigateTo('contact')} className="text-gray-400 hover:text-gray-500">Contact Us</button>
              <span className="text-gray-300">|</span>
              <button onClick={() => navigateTo('privacy')} className="text-gray-400 hover:text-gray-500">Privacy Policy</button>
              <span className="text-gray-300">|</span>
              <button onClick={() => navigateTo('faq')} className="text-gray-400 hover:text-gray-500">FAQ</button>
            </div>
            <div className="mt-8 md:mt-0 md:order-1">
              <p className="text-center text-base text-gray-400">&copy; 2025 SafeIMEI Nigeria. All rights reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    );
  }