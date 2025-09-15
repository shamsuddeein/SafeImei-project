const ShieldCheckIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>`;

function OfficerPortalLayout({ children, navigateTo, handleLogout }) {
  return (
    <div className="page min-h-screen bg-gray-100">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center gap-2 text-xl font-bold text-blue-600">
                <span dangerouslySetInnerHTML={{ __html: ShieldCheckIcon }} />
                <span>SafeIMEI Officer Portal</span>
              </div>
            </div>
            <div className="flex items-center">
              <button onClick={() => navigateTo('dashboard')} className="hidden sm:block text-sm font-medium text-gray-500 hover:text-gray-700 mr-4">Dashboard</button>
              <button onClick={handleLogout} className="text-sm font-medium text-red-500 hover:text-red-700">Logout</button>
            </div>
          </div>
        </div>
      </nav>
      <main>
        <div className="py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function Dashboard({ navigateTo, handleLogout }) {
  return (
    <OfficerPortalLayout navigateTo={navigateTo} handleLogout={handleLogout}>
      <div>
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Officer Dashboard</h1>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Reports This Month</dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">12</dd>
              </dl>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Pending Admin Review</dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">3</dd>
              </dl>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Recently Recovered</dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">1</dd>
              </dl>
            </div>
          </div>
        </div>
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
          <button onClick={() => navigateTo('createReport')} className="p-8 bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow text-center">
            <h2 className="text-xl font-bold text-gray-800">Create New Report</h2>
            <p className="text-gray-500 mt-2">File a new report for a stolen device.</p>
          </button>
          <button onClick={() => navigateTo('viewReports')} className="p-8 bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow text-center">
            <h2 className="text-xl font-bold text-gray-800">View Station Reports</h2>
            <p className="text-gray-500 mt-2">Review and manage reports filed by your station.</p>
          </button>
        </div>
      </div>
    </OfficerPortalLayout>
  );
}