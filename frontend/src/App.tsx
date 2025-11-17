import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { RFPList } from './components/RFPList';
import { RFPDetail } from './components/RFPDetail';
import { ApprovalInterface } from './components/ApprovalInterface';
import { ApprovalList } from './components/ApprovalList';
import { Exploration } from './components/Exploration';

function App() {
  return (
    <div>
      <nav>
        <Link to="/">RFPs</Link>
        <Link to="/approvals">Aprovações</Link>
        <Link to="/explore">Explorar</Link>
      </nav>
      
      <Routes>
        <Route path="/" element={<RFPList />} />
        <Route path="/rfp/:id" element={<RFPDetail />} />
        <Route path="/approvals" element={<ApprovalList />} />
        <Route path="/approvals/:approvalId" element={<ApprovalInterface />} />
        <Route path="/explore" element={<Exploration />} />
      </Routes>
    </div>
  );
}

export default App;

