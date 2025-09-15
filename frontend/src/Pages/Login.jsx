import { useState } from 'react';

export default function Login({ navigateTo }) {
  const [errorMessage, setErrorMessage] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    const stationId = e.target.elements.stationId.value;
    const password = e.target.elements.password.value;
    if (!stationId || !password) {
      setErrorMessage('Please enter both Station ID and Password.');
      return;
    }
    navigateTo('auth');
  };

  return (
    <div className="page min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Officer Portal Login</h2>
      </div>
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label htmlFor="stationId" className="block text-sm font-medium text-gray-700">Station ID</label>
              <div className="mt-1">
                <input id="stationId" name="stationId" type="text" required className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
              </div>
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
              <div className="mt-1">
                <input id="password" name="password" type="password" required className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
              </div>
            </div>
            <div className="text-sm text-red-600">{errorMessage}</div>
            <div>
              <button type="submit" className="w-full flex justify-center py-2 px-4 border rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">Login</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}