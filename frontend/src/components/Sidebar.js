import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronDownIcon, ChevronRightIcon, XMarkIcon } from '@heroicons/react/24/outline';

const Sidebar = ({ sidebarOpen, setSidebarOpen }) => {
  const location = useLocation();
  
  // State for expanded menu sections
  const [expandedSections, setExpandedSections] = useState({
    causelists: true,
    judgements: false
  });

  // Toggle section expansion
  const toggleSection = (section) => {
    setExpandedSections({
      ...expandedSections,
      [section]: !expandedSections[section]
    });
  };

  // Check if a route is active
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <>
      {/* Mobile sidebar overlay */}
      <div className={`fixed inset-0 z-40 md:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        {/* Background overlay */}
        <div 
          className="fixed inset-0 bg-gray-600 bg-opacity-75" 
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        ></div>
        
        {/* Sidebar panel */}
        <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white">
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              onClick={() => setSidebarOpen(false)}
            >
              <span className="sr-only">Close sidebar</span>
              <XMarkIcon className="h-6 w-6 text-white" aria-hidden="true" />
            </button>
          </div>
          
          {/* Mobile sidebar content */}
          <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
            <div className="flex-shrink-0 flex items-center px-4">
              <h1 className="text-xl font-bold text-court-blue">Court Data</h1>
            </div>
            <nav className="mt-5 px-2 space-y-1">
              {renderSidebarContent()}
            </nav>
          </div>
        </div>
        
        <div className="flex-shrink-0 w-14" aria-hidden="true">
          {/* Dummy element to force sidebar to shrink to fit close icon */}
        </div>
      </div>
      
      {/* Static sidebar for desktop */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex-1 flex flex-col min-h-0 border-r border-gray-200 bg-white">
            <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
              <div className="flex items-center flex-shrink-0 px-4">
                <h1 className="text-xl font-bold text-court-blue">Court Data</h1>
              </div>
              <nav className="mt-5 flex-1 px-2 space-y-1">
                {renderSidebarContent()}
              </nav>
            </div>
          </div>
        </div>
      </div>
    </>
  );

  function renderSidebarContent() {
    return (
      <>
        {/* Cause Lists Section */}
        <div>
          <button
            className={`w-full sidebar-item ${location.pathname.includes('/causelists') ? 'active' : ''}`}
            onClick={() => toggleSection('causelists')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span>Cause Lists</span>
            <span className="ml-auto">
              {expandedSections.causelists ? (
                <ChevronDownIcon className="h-4 w-4" />
              ) : (
                <ChevronRightIcon className="h-4 w-4" />
              )}
            </span>
          </button>
          
          {expandedSections.causelists && (
            <div className="sidebar-submenu">
              <Link 
                to="/causelists/delhi_hc" 
                className={`sidebar-item ${isActive('/causelists/delhi_hc') ? 'active' : ''}`}
              >
                Delhi HC
              </Link>
              <Link 
                to="/causelists/supreme_court" 
                className={`sidebar-item ${isActive('/causelists/supreme_court') ? 'active' : ''}`}
              >
                Supreme Court
              </Link>
              <Link 
                to="/causelists/bombay_hc" 
                className={`sidebar-item ${isActive('/causelists/bombay_hc') ? 'active' : ''}`}
              >
                Bombay HC
              </Link>
              <Link 
                to="/causelists/madras_hc" 
                className={`sidebar-item ${isActive('/causelists/madras_hc') ? 'active' : ''}`}
              >
                Madras HC
              </Link>
            </div>
          )}
        </div>
        
        {/* Judgements Section */}
        <div>
          <button
            className={`w-full sidebar-item ${location.pathname.includes('/judgements') ? 'active' : ''}`}
            onClick={() => toggleSection('judgements')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
            <span>Judgements</span>
            <span className="ml-auto">
              {expandedSections.judgements ? (
                <ChevronDownIcon className="h-4 w-4" />
              ) : (
                <ChevronRightIcon className="h-4 w-4" />
              )}
            </span>
          </button>
          
          {expandedSections.judgements && (
            <div className="sidebar-submenu">
              <Link 
                to="/judgements/delhi_hc" 
                className={`sidebar-item ${isActive('/judgements/delhi_hc') ? 'active' : ''}`}
              >
                Delhi HC
              </Link>
              <Link 
                to="/judgements/supreme_court" 
                className={`sidebar-item ${isActive('/judgements/supreme_court') ? 'active' : ''}`}
              >
                Supreme Court
              </Link>
              <Link 
                to="/judgements/bombay_hc" 
                className={`sidebar-item ${isActive('/judgements/bombay_hc') ? 'active' : ''}`}
              >
                Bombay HC
              </Link>
              <Link 
                to="/judgements/madras_hc" 
                className={`sidebar-item ${isActive('/judgements/madras_hc') ? 'active' : ''}`}
              >
                Madras HC
              </Link>
            </div>
          )}
        </div>
      </>
    );
  }
};

export default Sidebar;
