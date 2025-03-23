import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { format, addDays, subDays } from 'date-fns';
import { ChevronLeftIcon, ChevronRightIcon, ChevronUpIcon, ChevronDownIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';
import { getMockCauseLists } from '../services/api';

const CauseListView = ({ court: propCourt }) => {
  const { court: paramCourt } = useParams();
  const court = paramCourt || propCourt || 'delhi_hc';
  
  // State for selected date and week range
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [weekDates, setWeekDates] = useState([]);
  
  // State for expanded court sections
  const [expandedCourts, setExpandedCourts] = useState({});
  
  // State for filter dropdown
  const [filterOpen, setFilterOpen] = useState(false);
  
  // State for tab selection
  const [activeTab, setActiveTab] = useState('cases');
  
  // State for cause lists data
  const [causeLists, setCauseLists] = useState([]);
  
  // State for loading status
  const [loading, setLoading] = useState(true);
  
  // Generate week dates when selected date changes
  useEffect(() => {
    const dates = [];
    // Find the start of the week (Sunday)
    const dayOfWeek = selectedDate.getDay();
    const startDate = subDays(selectedDate, dayOfWeek);
    
    // Generate 7 days
    for (let i = 0; i < 7; i++) {
      dates.push(addDays(startDate, i));
    }
    
    setWeekDates(dates);
  }, [selectedDate]);
  
  // Fetch cause lists when court or date changes
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // In a real implementation, this would be an API call
        // For now, we'll use mock data
        const data = getMockCauseLists(court);
        
        // Initialize expanded state for all courts
        const expandedState = {};
        data.forEach(courtData => {
          expandedState[courtData.court] = true;
        });
        
        setExpandedCourts(expandedState);
        setCauseLists(data);
      } catch (error) {
        console.error('Error fetching cause lists:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [court, selectedDate]);
  
  // Toggle court expansion
  const toggleCourt = (court) => {
    setExpandedCourts({
      ...expandedCourts,
      [court]: !expandedCourts[court]
    });
  };
  
  // Navigate to previous week
  const goToPreviousWeek = () => {
    setSelectedDate(subDays(selectedDate, 7));
  };
  
  // Navigate to next week
  const goToNextWeek = () => {
    setSelectedDate(addDays(selectedDate, 7));
  };
  
  // Select a specific date
  const selectDate = (date) => {
    setSelectedDate(date);
  };
  
  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
        {/* Date navigation */}
        <div className="flex items-center justify-between mb-6">
          <button 
            onClick={goToPreviousWeek}
            className="p-2 rounded-full bg-white shadow hover:bg-gray-50"
          >
            <ChevronLeftIcon className="h-5 w-5 text-gray-500" />
          </button>
          
          <div className="flex-1 max-w-3xl mx-4">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="grid grid-cols-7">
                {weekDates.map((date, index) => {
                  const isSelected = format(date, 'yyyy-MM-dd') === format(selectedDate, 'yyyy-MM-dd');
                  const dayName = format(date, 'EEE').toUpperCase();
                  const dayNumber = format(date, 'd MMM');
                  
                  return (
                    <button
                      key={index}
                      onClick={() => selectDate(date)}
                      className={`py-2 ${isSelected ? 'bg-court-blue text-white' : 'bg-white hover:bg-gray-50'}`}
                    >
                      <div className="text-xs font-medium">{dayName}</div>
                      <div className={`text-sm ${isSelected ? 'text-white' : 'text-gray-900'}`}>{dayNumber}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
          
          <button 
            onClick={goToNextWeek}
            className="p-2 rounded-full bg-white shadow hover:bg-gray-50"
          >
            <ChevronRightIcon className="h-5 w-5 text-gray-500" />
          </button>
        </div>
        
        {/* Filters and tabs */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="p-4 flex items-center justify-between">
            <div className="relative">
              <button 
                onClick={() => setFilterOpen(!filterOpen)}
                className="flex items-center text-sm text-gray-700 font-medium hover:text-court-blue"
              >
                <span>Sort By</span>
                <ChevronDownIcon className="ml-1 h-4 w-4" />
              </button>
              
              {filterOpen && (
                <div className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
                  <div className="py-1">
                    <button className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left">Court Name</button>
                    <button className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left">Case Number</button>
                    <button className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left">Date Added</button>
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex space-x-4">
              <div className="bg-gray-100 rounded-md">
                <nav className="flex">
                  <button
                    onClick={() => setActiveTab('cases')}
                    className={`day-tab ${activeTab === 'cases' ? 'active' : ''}`}
                  >
                    Cases
                  </button>
                  <button
                    onClick={() => setActiveTab('applications')}
                    className={`day-tab ${activeTab === 'applications' ? 'active' : ''}`}
                  >
                    Applications
                  </button>
                </nav>
              </div>
              
              <button className="p-2 rounded-md hover:bg-gray-100">
                <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-500" />
              </button>
            </div>
          </div>
        </div>
        
        {/* Loading state */}
        {loading && (
          <div className="text-center py-10">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-court-blue"></div>
            <p className="mt-2 text-gray-500">Loading cause lists...</p>
          </div>
        )}
        
        {/* No data state */}
        {!loading && causeLists.length === 0 && (
          <div className="text-center py-10">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No cause lists found</h3>
            <p className="mt-1 text-sm text-gray-500">No cause lists are available for this date.</p>
          </div>
        )}
        
        {/* Court cards */}
        {!loading && causeLists.length > 0 && (
          <div className="space-y-4">
            {causeLists.map((courtData, courtIndex) => (
              <div key={courtIndex} className="court-card">
                <div 
                  className="court-card-header"
                  onClick={() => toggleCourt(courtData.court)}
                >
                  <div className="flex items-center space-x-4">
                    <h3 className="text-sm font-medium text-gray-900">{courtData.court}</h3>
                    <span className="text-sm text-gray-500">{courtData.courtNo}</span>
                    <span className="text-sm text-gray-500">{courtData.bench}</span>
                  </div>
                  
                  <button>
                    {expandedCourts[courtData.court] ? (
                      <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                    ) : (
                      <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                    )}
                  </button>
                </div>
                
                {expandedCourts[courtData.court] && (
                  <div>
                    {courtData.cases.map((caseData, caseIndex) => (
                      <div key={caseIndex} className="case-item">
                        <div className="flex justify-between items-start mb-2">
                          <div className="text-sm font-medium text-gray-900">{caseData.caseNumber}</div>
                          <button className="text-gray-400 hover:text-gray-500">
                            <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                              <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                            </svg>
                          </button>
                        </div>
                        
                        <h4 className="text-sm text-gray-900 mb-2">{caseData.title}</h4>
                        
                        <div className="flex flex-wrap gap-2 mb-3">
                          {caseData.tags && caseData.tags.map((tag, tagIndex) => (
                            <span key={tagIndex} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {tag}
                            </span>
                          ))}
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                          <div>
                            <p><span className="font-medium">Item:</span> {caseData.itemNumber}</p>
                            <p><span className="font-medium">File Number:</span> {caseData.fileNumber}</p>
                            <p><span className="font-medium">Causelist:</span> {caseData.causeList}</p>
                          </div>
                          <div>
                            <p><span className="font-medium">Petitioner Adv:</span> {caseData.petitionerAdv}</p>
                            <p><span className="font-medium">Respondent Adv:</span> {caseData.respondentAdv}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CauseListView;
