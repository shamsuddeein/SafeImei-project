import { useState } from 'react';

export default function Home() {
  const [imeiResult, setImeiResult] = useState('');
  const [loading, setLoading] = useState(false);

  const handleImeiCheck = (e) => {
    e.preventDefault();
    const imei = e.target.elements['imei-input'].value;
    setLoading(true);

    setTimeout(() => {
      let result = {};
      if (imei === '123456789012345') {
        result = { status: 'stolen', message: 'This device has been reported stolen. Do not buy!' };
      } else {
        result = { status: 'safe', message: 'This device has not been reported stolen. Safe to buy!' };
      }

      const bgColor = result.status === 'stolen' ? 'bg-red-100 border-l-4 border-red-500 text-red-700' : 'bg-green-100 border-l-4 border-green-500 text-green-700';
      const title = result.status === 'stolen' ? 'Warning!' : 'All Clear!';

      setImeiResult(
        `<div class="p-4 rounded-md text-left ${bgColor}"><p class="font-bold">${title}</p><p>${result.message}</p></div>`
      );
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="page pt-16">
      <header className="bg-white">
        <div className="max-w-7xl mx-auto py-20 px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">Buy Used Phones with Confidence.</h1>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500">Instantly check if a phone has been reported stolen with Nigeria's official IMEI database.</p>
          <div className="mt-10 max-w-xl mx-auto">
            <form onSubmit={handleImeiCheck} className="sm:flex sm:gap-2">
              <input id="imei-input" type="text" maxLength="15" placeholder="Enter 15-digit IMEI number" className="w-full px-5 py-4 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg" required />
              <button type="submit" disabled={loading} className="mt-3 w-full sm:mt-0 sm:w-auto sm:flex-shrink-0 inline-flex items-center justify-center px-6 py-4 border border-transparent text-lg font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
                {loading ? 'Checking...' : 'Check IMEI'}
              </button>
            </form>
            <div id="imei-result" className="mt-6" dangerouslySetInnerHTML={{ __html: imeiResult }} />
          </div>
        </div>
      </header>
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">How It Works</h2>
            <p className="mt-2 text-3xl font-extrabold text-gray-900 tracking-tight sm:text-4xl">A Simple Process for Peace of Mind</p>
          </div>
          <div className="mt-12 grid gap-10 md:grid-cols-3">
            <div className="text-center p-6 bg-white rounded-lg shadow-md"><div className="text-4xl mb-4">1.</div><h3 className="text-xl font-bold">Report a Theft</h3><p className="mt-2 text-gray-500">Victims report their stolen device at an authorized police station.</p></div>
            <div className="text-center p-6 bg-white rounded-lg shadow-md"><div className="text-4xl mb-4">2.</div><h3 className="text-xl font-bold">We Verify & Log</h3><p className="mt-2 text-gray-500">Police verify the report and add the IMEI to our secure national database.</p></div>
            <div className="text-center p-6 bg-white rounded-lg shadow-md"><div className="text-4xl mb-4">3.</div><h3 className="text-xl font-bold">You Check Before Buying</h3><p className="mt-2 text-gray-500">Enter the phone's IMEI on our site to see its status instantly.</p></div>
          </div>
        </div>
      </section>
    </div>
  );
}