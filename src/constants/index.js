import {
    mobile,
    backend,
    creator,
    web,
    javascript,
    html,
    css,
    reactjs,
    nodejs,
    mongodb,
    git,
    figma,
    firebase,
    java,
    python,
    gitam,
    genesis,
    threejs,
    shriya,
    manogyna,
    emi,
    blood,
    digit
  } from "../assets";
  
  export const navLinks = [
    {
      id: "about",
      title: "About",
    },
    {
      id: "work",
      title: "Work",
    },
    {
      id: "contact",
      title: "Contact",
    },
  ];
  
  const services = [
    {
      title: "Tensorflow Developer",
      icon: web,
    },
    {
      title: "Flutter Developer",
      icon: mobile,
    },
    {
      title: "Vuejs Developer",
      icon: backend,
    },
    {
      title: "Blog Writer",
      icon: creator,
    },
    {
      title: "Leetcoder",
      icon: web,
    }
  ];
  
  const technologies = [
    {
      name : firebase,
      icon : firebase,
    },
    {
      name : java,
      icon : java,
    },
    {
      name: "Python",
      icon : python,
    },
    
    {
      name: "HTML 5",
      icon: html,
    },
    {
      name: "CSS 3",
      icon: css,
    },
    {
      name: "JavaScript",
      icon: javascript,
    },
    {
      name: "React JS",
      icon: reactjs,
    },
    {
      name: "Node JS",
      icon: nodejs,
    },
    {
      name: "MongoDB",
      icon: mongodb,
    },
    {
      name: "Three JS",
      icon: threejs,
    },
    {
      name: "git",
      icon: git,
    },
    {
      name: "figma",
      icon: figma,
    },
  ];
  
  const experiences = [
    {
      title: "Full Stack Web Developer",
      company_name: "Genesis Technologies",
      icon: genesis,
      iconBg: "#383E56",
      date: "May 2023 - June 2023",
      points: [
        "Developing a HRMS application using Vuejs, nodejs, mongodb and Quasar framework.",
        "Creating a custom PDF plugin to view bills and invoices.",
        "Troubleshooting UI/UX of the application and fixing bugs."
      ],
    },
    {
      title: "Computer Vision Engineer",
      company_name: "Center for Autonomous Systems, Gitam",
      icon: gitam,
      iconBg: "#E6DEDD",
      date: "April 2022 - September 2022",
      points: [
        "Worked on computer vision models for object detection and tracking such as Yolov5, SSD",
        "Conducted and coordinated a 3-day workshop on Hands-on robotics and Actuator programming for 50+ students in Gitam Bangalore Campus.",
        "Represented CAS Gitam on National Innovation Day 2022"
      ],
    },

  ];
  
  const testimonials = [
    {
      testimonial:
        "Sriram is proficient in Vue, Flutter, TensorFlow and his contributions extend to sharing valuable knowledge through tech blogs",
      name: "G V Shriya",
      designation: "Student",
      company: "Gitam Deemed University",
      image: shriya,
    },

    {
      testimonial:
        "Sriram Bharadwaj's coding and problem-solving skills are exceptional. His passion for the AI/ML domain is truly inspiring. He is a standout talent in this field, and his dedication is unquestionable.",
      name: "K Manogyna",
      designation: "Student",
      company: "Gitam Deemed University",
      image: manogyna,
    },
  ];
  
  const projects = [
    {
      name: "Rapid Digit Tester",
      description:
        "An Android based application that enables Deep Learning developers to rapidly test the performance of their digit recognition models on a mobile device screen. The application is built using Android and Tensorflow Lite.",
  
      tags: [
        {
          name: "Tensorflow",
          color: "orange-text-gradient",
        },
        {
          name: "Android",
          color: "green-text-gradient",
        },
        {
          name: "Deep Learning",
          color: "blue-text-gradient",
        },
      ],
      image: digit,
      source_code_link: "https://github.com/SriramBharadwaj1/mnist_digit_mobile",
    },

    {
      name: "Blood Alert",
      description:
        "A Firebase powered application that notifies willing donors about emergency blood requirements. The applications uses smart-distance logic and push notifications to alert donors about blood requirements in their vicinity. The application is built using Flutter and Firebase.",
  
      tags: [
        {
          name: "Flutter",
          color: "blue-text-gradient",
        },
        {
          name: "Firebase",
          color: "orange-text-gradient",
        },
      ],
      image: blood,
      source_code_link: "https://github.com/SriramBharadwaj1/BloodAlert",
    },

    {
      name: "EMI calculator",
      description:
        "A jQuery Powered PWA, that calculates monthly installments and amounts, all represented beautifylly in a JQuery DataTable. The application is built using HTML, CSS, JavaScript and jQuery.",
  
      tags: [
        {
          name: "JQuery",
          color: "blue-text-gradient",
        },
        {
          name: "PWA",
          color: "black-text-gradient",
        },
      ],
      image: emi,
      source_code_link: "https://github.com/SriramBharadwaj1/emi",
    },
    
  ];
  
  export { services, technologies, experiences, testimonials, projects };