import { useState } from 'react';

const deviceBrands = ["Select Brand...", "Samsung", "Apple", "Tecno", "Infinix", "Xiaomi", "Nokia", "itel", "Oppo", "Vivo", "Realme", "Gionee", "Huawei", "Other"];
const deviceColors = ["Select Color...", "Black", "White", "Blue", "Gold", "Silver", "Red", "Green", "Gray", "Purple", "Rose Gold", "Other"];
const incidentTypes = ["Select Type...", "Snatching (in transit)", "Armed Robbery", "Burglary (house/office)", "Misplaced / Lost", "Pickpocketing", "Other"];

export default function CreateReport({ showModal }) {
  const [step, setStep] = useState(1);
  const [reportData, setReportData] = useState({});
  const [validationError, setValidationError] = useState({});

  const titles = ["Personal Information", "Device Information", "Incident Information", "Proof of Ownership", "Details Confirmation"];

  const handleNext = (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const newData = {};
    formData.forEach((value, key) => {
      newData[key] = value;
    });

    // Simple validation for required fields
    if (step === 1 && (!newData.fullName || !newData.phoneNumber)) {
      setValidationError({ field: 'fullName', message: 'Full name and phone number are required.' });
      return;
    }
    if (step === 2 && (!newData.imei || !newData.brand || !newData.model)) {
      setValidationError({ field: 'imei', message: 'IMEI, brand, and model are required.' });
      return;
    }
    // Add more validation for other steps as needed

    setReportData({ ...reportData, ...newData });
    setStep(step + 1);
    setValidationError({});
  };

  const handlePrev = () => {
    setStep(step - 1);
    setValidationError({});
  };

  const handleSubmitReport = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const transactionRef = formData.get('transactionRef');
    if (!transactionRef) {
      setValidationError({ field: 'transactionRef', message: 'Transaction Reference is required.' });
      return;
    }

    const finalReport = { ...reportData, transactionRef };
    console.log("Submitting report:", finalReport);
    showModal('Report Submitted', 'The report has been successfully submitted for review.');
    setStep(1);
    setReportData({});
  };
  
  const formInput = (label, id, props = "") => (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="mt-1">
        <input id={id} name={id} value={reportData[id] || ''} onChange={(e) => setReportData({...reportData, [id]: e.target.value})} {...props} className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
      </div>
      {validationError.field === id && <p className="text-xs text-red-600 mt-1">{validationError.message}</p>}
    </div>
  );
  
  const formSelect = (label, id, options, props = "") => (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="mt-1">
        <select id={id} name={id} value={reportData[id] || ''} onChange={(e) => setReportData({...reportData, [id]: e.target.value})} {...props} className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white">
          {options.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>
    </div>
  );
  
  const formTextArea = (label, id) => (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700">{label}</label>
      <textarea id={id} name={id} rows="3" value={reportData[id] || ''} onChange={(e) => setReportData({...reportData, [id]: e.target.value})} className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"></textarea>
    </div>
  );
  
  const navButtons = (showBack = true, nextLabel = "Next") => (
    <div className="flex gap-4 mt-6">
      {showBack && <button type="button" onClick={handlePrev} className="w-full justify-center py-2 px-4 border border-gray-300 rounded-md text-sm bg-white hover:bg-gray-50">Back</button>}
      <button type="submit" className={`w-full justify-center py-2 px-4 border rounded-md text-sm text-white ${nextLabel === 'Submit Report' ? 'bg-green-600 hover:bg-green-700' : 'bg-blue-600 hover:bg-blue-700'}`}>{nextLabel}</button>
    </div>
  );

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <form onSubmit={handleNext} className="space-y-4">
            {formInput("Full Name", "fullName", { required: true })}
            {formInput("Phone Number", "phoneNumber", { type: "tel", required: true })}
            {formInput("Email Address (Optional)", "email", { type: "email" })}
            {formTextArea("Address", "address")}
            {navButtons(false)}
          </form>
        );
      case 2:
        return (
          <form onSubmit={handleNext} className="space-y-4">
            {formInput("IMEI Number", "imei", { maxLength: 15, required: true })}
            {formSelect("Device Brand", "brand", deviceBrands, { required: true })}
            {formInput("Device Model Number", "model", { required: true })}
            {formSelect("Device Color", "color", deviceColors)}
            {formInput("Device Phone Number (Last Used)", "devicePhone", { type: "tel" })}
            {navButtons()}
          </form>
        );
      case 3:
        return (
          <form onSubmit={handleNext} className="space-y-4">
            {formInput("Date of Incident", "date", { type: "date", required: true })}
            {formInput("Time of Incident", "time", { type: "time", required: true })}
            {formSelect("Type of Incident", "type", incidentTypes, { required: true })}
            {formTextArea("Last Seen Location / Address", "location")}
            {navButtons()}
          </form>
        );
      case 4:
        return (
          <form onSubmit={handleNext} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Owner's Passport / ID</label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48"><path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>
                  <div className="flex text-sm text-gray-600">
                    <label htmlFor="ownerId" className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500">
                      <span>Upload a file</span>
                      <input id="ownerId" name="ownerId" type="file" className="sr-only" />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">PNG, JPG up to 10MB</p>
                </div>
              </div>
            </div>
            {navButtons()}
          </form>
        );
      case 5:
        const detailItem = (label, value) => (
          <div className="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">{label}</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{value || 'Not provided'}</dd>
          </div>
        );
        return (
          <>
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5"><h3 className="text-lg font-medium text-gray-900">Confirm Report Details</h3></div>
              <div className="border-t border-gray-200">
                <dl className="divide-y divide-gray-200">
                  {detailItem("Full Name", reportData.fullName)}
                  {detailItem("Phone Number", reportData.phoneNumber)}
                  {detailItem("IMEI", reportData.imei)}
                  {detailItem("Device", `${reportData.brand || ''} ${reportData.model || ''}`)}
                  {detailItem("Date of Incident", reportData.date)}
                  {/* Note: File names are not saved in state in this simple example */}
                </dl>
              </div>
            </div>
            <form onSubmit={handleSubmitReport} className="mt-6 space-y-4">
              {formInput("Transaction Reference", "transactionRef", { required: true, placeholder: "Enter payment reference" })}
              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input id="terms" type="checkbox" required className="h-4 w-4 text-blue-600 border-gray-300 rounded" />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="terms" className="font-medium text-gray-700">Acceptance of Terms</label>
                  <p className="text-gray-500">You confirm the details are accurate and agree to the Terms & Conditions.</p>
                </div>
              </div>
              {navButtons(true, 'Submit Report')}
            </form>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-2">Create New Report</h1>
      <h2 className="text-lg text-gray-600 mb-6">{titles[step - 1]}</h2>
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <div className="mb-8">
          <div className="flex justify-between mb-1"><span className="text-base font-medium text-blue-700">Step {step} of 5</span></div>
          <div className="w-full bg-gray-200 rounded-full h-2.5"><div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${(step / 5) * 100}%` }}></div></div>
        </div>
        {renderStep()}
      </div>
    </div>
  );
}