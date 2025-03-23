// API service for fetching court data

// Base API URL - adjust this to match your backend API
const API_BASE_URL = 'http://localhost:8000';

// Fetch cause lists for a specific court and date
export const fetchCauseLists = async (court, date) => {
  try {
    // Format date as YYYY-MM-DD if provided
    const formattedDate = date ? formatDate(date) : formatDate(new Date());
    const response = await fetch(`${API_BASE_URL}/courts/${court}/cause_lists/${formattedDate}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching cause lists: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch cause lists:', error);
    // Fall back to mock data in development
    if (process.env.NODE_ENV === 'development') {
      console.log('Using mock data for cause lists');
      return getMockCauseLists(court);
    }
    return { error: error.message };
  }
};

// Fetch judgments for a specific court and date range
export const fetchJudgments = async (court, startDate, endDate) => {
  try {
    // Format dates as YYYY-MM-DD if provided
    const startDateParam = startDate ? `&startDate=${formatDate(startDate)}` : '';
    const endDateParam = endDate ? `&endDate=${formatDate(endDate)}` : '';
    
    const response = await fetch(
      `${API_BASE_URL}/judgments?court=${court}${startDateParam}${endDateParam}`
    );
    
    if (!response.ok) {
      throw new Error(`Error fetching judgments: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch judgments:', error);
    return { error: error.message };
  }
};

// Fetch available courts
export const fetchCourts = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/courts`);
    
    if (!response.ok) {
      throw new Error(`Error fetching courts: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch courts:', error);
    // Return mock courts in development
    if (process.env.NODE_ENV === 'development') {
      console.log('Using mock data for courts');
      return [
        { id: 1, name: 'Delhi High Court', code: 'delhi_hc' }
      ];
    }
    return { error: error.message };
  }
};

// Fetch available dates for a court
export const fetchAvailableDates = async (court) => {
  try {
    const response = await fetch(`${API_BASE_URL}/courts/${court}/dates`);
    
    if (!response.ok) {
      throw new Error(`Error fetching available dates: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.dates || [];
  } catch (error) {
    console.error('Failed to fetch available dates:', error);
    // Return mock dates in development
    if (process.env.NODE_ENV === 'development') {
      console.log('Using mock data for dates');
      const today = new Date();
      return [
        formatDate(today),
        formatDate(new Date(today.setDate(today.getDate() - 1))),
        formatDate(new Date(today.setDate(today.getDate() - 1)))
      ];
    }
    return [];
  }
};

// Helper function to format date as YYYY-MM-DD
const formatDate = (date) => {
  if (!date) return '';
  
  if (typeof date === 'string') {
    // If already in ISO format, return the date part
    if (date.match(/^\d{4}-\d{2}-\d{2}/)) {
      return date.substring(0, 10);
    }
  }
  
  // Otherwise, format the date object
  const d = new Date(date);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

// For development/demo purposes - mock data
export const getMockCauseLists = (court) => {
  // This function returns mock data based on the data structure in our scrapers
  const mockData = {
    delhi_hc: [
      {
        court: 'DELHI HIGH COURT',
        courtNo: 'COURT NO. 1',
        bench: 'BENCH - THE CHIEF JUSTICE | MR. JUSTICE SIDDHARTH MRIDUL',
        cases: [
          {
            caseNumber: 'W.P.(C) / 12345 / 2023',
            title: 'JOHN DOE vs GOVERNMENT OF NCT DELHI',
            tags: ['Daily list', 'Constitutional'],
            itemNumber: '1',
            fileNumber: '123',
            causeList: 'Daily List',
            petitionerAdv: 'Adv. Rajesh Kumar(P-1)',
            respondentAdv: 'Adv. Priya Singh(R-1)'
          },
          {
            caseNumber: 'W.P.(C) / 67890 / 2023',
            title: 'ABC CORPORATION vs INCOME TAX DEPARTMENT',
            tags: ['Daily list', 'Tax matter'],
            itemNumber: '2',
            fileNumber: '456',
            causeList: 'Daily List',
            petitionerAdv: 'Adv. Sunil Sharma(P-1)',
            respondentAdv: 'Adv. Deepak Gupta(R-1)'
          }
        ]
      },
      {
        court: 'DELHI HIGH COURT',
        courtNo: 'COURT NO. 2',
        bench: 'BENCH - MR. JUSTICE RAJIV SHAKDHER | MS. JUSTICE TARA VITASTA GANJU',
        cases: [
          {
            caseNumber: 'CS(COMM) / 789 / 2023',
            title: 'TECH INNOVATIONS PVT LTD vs FUTURE ELECTRONICS LTD',
            tags: ['Daily list', 'Commercial'],
            itemNumber: '10',
            fileNumber: '789',
            causeList: 'Daily List',
            petitionerAdv: 'Adv. Amit Sibal(P-1)',
            respondentAdv: 'Adv. Gopal Subramanium(R-1)'
          }
        ]
      }
    ],
    supreme_court: [
      {
        court: 'SUPREME COURT',
        courtNo: 'COURT NO. 1',
        bench: 'BENCH - THE CHIEF JUSTICE | MR. JUSTICE J.B. PARDIWALA | MR. JUSTICE MANOJ MISRA',
        cases: [
          {
            caseNumber: 'SLP (Civil) / 21838 / 2019',
            title: 'COMMISSIONER OF CENTRAL EXCISE, COMMISSIONERATE, PUNJAB vs M/S NESTLE INDIA LIMITED GURGAON',
            tags: ['Weekly tentative', 'Bombay high court'],
            itemNumber: '63',
            fileNumber: '782',
            causeList: 'Weekly List',
            petitionerAdv: 'Raj Bahadur Yadav(P-1)',
            respondentAdv: 'Charanya Lakshmikumaran(R-1)'
          }
        ]
      }
    ],
    bombay_hc: [
      {
        court: 'BOMBAY HIGH COURT',
        courtNo: 'COURT NO. 2',
        bench: 'BENCH - SHRI JUSTICE G. S. KULKARNI | SHRI JUSTICE SOMASEKHAR SUNDARESAN',
        cases: [
          {
            caseNumber: 'Income Tax Appeal (Original) / 1041 / 2012',
            title: 'THE BOARD OF CONTROL FOR CRICKET IN INDIA, vs THE ASSISTANT COMMISSIONER OF INCOME TAX, CENTRAL CIRCLE 35, MUMBAI.',
            tags: [],
            itemNumber: '12',
            fileNumber: '456',
            causeList: 'Daily List',
            petitionerAdv: 'Harish Salve(P-1)',
            respondentAdv: 'Tushar Mehta(R-1)'
          }
        ]
      }
    ]
  };
  
  return mockData[court] || [];
};

// Create API service object
const apiService = {
  fetchCauseLists,
  fetchJudgments,
  fetchCourts,
  fetchAvailableDates,
  getMockCauseLists
};

export default apiService;
