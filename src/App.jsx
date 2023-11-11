import { BrowserRouter } from "react-router-dom";
import { About, Contact, Experience, Feedbacks, Navbar, Tech, Works, StarsCanvas, Hero} from './components';


console.log('hi');
const App = () => {

  return (
    <BrowserRouter>
    <div>
      <a href={process.env.PUBLIC_URL + '../public/sitemap.xml'}></a>
      <a href={process.env.PUBLIC_URL + '../public/robots.txt'}></a>
    </div>
      <div className="relative z-0 bg-primary">
        <div className = 'bg-hero-pattern bg-cover bg-center bg-no-repeat'>
          <Navbar />
          <Hero />
        </div>
        

        <About />
        <Experience />
        <Tech />
        <Works />
        <Feedbacks />

        <div className = 'relative z-0'>
          <Contact />
          <StarsCanvas />
        </div>
        
      </div>
    </BrowserRouter>
  )
}

export default App
