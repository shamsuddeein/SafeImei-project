import { useState } from 'react';

// Mock data
const stationReports = [
  { id: 'RPT001', imei: '123456789012345', brand: 'Samsung', model: 'Galaxy S22', date: '2025-09-10', status: 'Stolen' },
  { id: 'RPT002', imei: '987654321098765', brand: 'Apple', model: 'iPhone 15 Pro', date: '2025-09-08', status: 'Stolen' },
  { id: 'RPT003', imei: '555566667777888', brand: 'Tecno', model: 'Camon 20', date: '2025-09-05', status: 'Recovered' },
  { id: 'RPT004', imei: '112233445566778', brand: 'Infinix', model: 'Note 30', date: '2025-09-02', status: 'Stolen' },
];

export default function ViewReports({ navigateTo }) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredReports = stationReports.filter(report =>
    report.imei.includes(searchTerm) ||
    report.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.model.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div className="mb-5">
        <button onClick={() => navigateTo('dashboard')} className="inline-flex items-center text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          Back to Dashboard
        </button>
      </div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Station Reports</h1>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <input type="search" id="report-search" placeholder="Search by IMEI..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
        </div>
      </div>
      <div className="mt-8 flex flex-col">
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">IMEI</th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Device</th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Date Reported</th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {filteredReports.length > 0 ? (
                    filteredReports.map(report => (
                      <tr key={report.id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{report.imei}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{report.brand} {report.model}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{report.date}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${report.status === 'Stolen' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                            {report.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="text-center text-gray-500 py-10">No reports found.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}