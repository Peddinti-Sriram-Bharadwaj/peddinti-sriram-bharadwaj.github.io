import { useState, useRef} from 'react';
import {motion} from 'framer-motion';
import emailjs from '@emailjs/browser';

import {styles} from '../styles';
import {EarthCanvas} from './canvas';
import {SectionWrapper} from '../hoc';
import {slideIn} from '../utils/motion';


//GC8-XzbfUOU9EkFfD
//template_l5e2wnr
//service_zn83x1y


const Contact = () => {

  const formRef = useRef();
  const [form, setForm] = useState({
    name: '',
    email: '',
    message: ''
  })

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const {name, value} = e.target;
    setForm({...form, [name]: value});

  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    emailjs.send(
      'service_zn83x1y', 
      'template_l5e2wnr', 
      {
        from_name: form.name,
        to_name: 'Sriram Bharadwaj',
        from_email: form.email,
        to_email: 'sriram921@gmail.com',
        message: form.message,
      }, 

      'uGC8-XzbfUOU9EkFfD'
      )

    .then((result) => {
      setLoading(false);
      alert('Thank You! I will get back to you as soon as possible');

      setForm({
        name: '',
        email: '',
        message: ''
      })
    }, (error) => {
      setLoading(false);
      console.log(error.text);
      alert('Opps! Something went wrong. Please try again');
    });
  };

  return (
    <div className = 'xl:mt-12 xl:flex-row flex-col-reverse flex gap-10 overflow-hidden'>
      <motion.div
      variants = {slideIn('left', 'tween', 0.5, 1)}
      className = 'flex-[0.75] bg-black-100 p-8 rounded-2xl'>
        <p className = {styles.sectionSubText}>Get in touch</p>
        <h3 className = {styles.sectionHeadText} >Contact.</h3>

        <form
        ref = {formRef}
        onSubmit = {handleSubmit}
        className = 'mt-12 flex flex-col gap-8'>
      <label className = 'flex flex-col'>
        <span className = 'text-white font-medium mb-4'>your Name</span>
        <input 
        type = 'text'
        name = 'name'
        value = {form.name}
        onChange = {handleChange}
        placeholder = "What's your name?"
        className = 'bg-tertiary py-4 px-6 placeholder:text-scondary text-white rounded-lg outlined-none border-none font-medium'/>
      </label>

      <label className = 'flex flex-col'>
        <span className = 'text-white font-medium mb-4'>your Email</span>
        <input 
        type = 'email'
        name = 'email'
        value = {form.email}
        onChange = {handleChange}
        placeholder = "What's your Email?"
        className = 'bg-tertiary py-4 px-6 placeholder:text-scondary text-white rounded-lg outlined-none border-none font-medium'/>
      </label>

      <label className = 'flex flex-col'>
        <span className = 'text-white font-medium mb-4'>your Message</span>
        <textarea 
        rows = '7'
        name = 'message'
        value = {form.message}
        onChange = {handleChange}
        placeholder = "What do you want to say"
        className = 'bg-tertiary py-4 px-6 placeholder:text-scondary text-white rounded-lg outlined-none border-none font-medium'/>
      </label>

      <button
      type = 'submit'
      className = 'bg-tertiary py-3 px-8 outline-none w-fit text-white font-bold shadow-md shadow-primary rounded-xl'>
        {loading? 'Sending...' : 'Send'}

      </button>

        </form>

      </motion.div>

      <motion.div
      variants = {slideIn('right', 'tween', 0.5, 1)}
      className = 'xl:flex-1 xl:h-auto md:h-[550px] h-[350px]'
      >

        <EarthCanvas/>

      </motion.div>
    </div>
  )
}

export default SectionWrapper(Contact, 'contact');