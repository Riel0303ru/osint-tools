import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout';
import DashboardPage from './pages/DashboardPage';
import UsernamePage from './pages/UsernamePage';
import EmailPage from './pages/EmailPage';
import DomainPage from './pages/DomainPage';
import IPPage from './pages/IPPage';
import PhonePage from './pages/PhonePage';
import CompanyPage from './pages/CompanyPage';
import ImagePage from './pages/ImagePage';
import DocumentPage from './pages/DocumentPage';
import VideoPage from './pages/VideoPage';
import DarkWebPage from './pages/DarkWebPage';
import CorrelationPage from './pages/CorrelationPage';
import GraphPage from './pages/GraphPage';
import AIPage from './pages/AIPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="username" element={<UsernamePage />} />
          <Route path="email" element={<EmailPage />} />
          <Route path="domain" element={<DomainPage />} />
          <Route path="ip" element={<IPPage />} />
          <Route path="phone" element={<PhonePage />} />
          <Route path="company" element={<CompanyPage />} />
          <Route path="image" element={<ImagePage />} />
          <Route path="document" element={<DocumentPage />} />
          <Route path="video" element={<VideoPage />} />
          <Route path="darkweb" element={<DarkWebPage />} />
          <Route path="correlation" element={<CorrelationPage />} />
          <Route path="graph" element={<GraphPage />} />
          <Route path="ai" element={<AIPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
