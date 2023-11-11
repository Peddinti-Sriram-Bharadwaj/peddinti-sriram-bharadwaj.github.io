import fs from 'fs';

const fs = require('fs');

// List of routes
const routes = [
    '/',
    '/about',
    '/experience',
    '/tech',
    '/works',
    '/feedbacks',
    '/contact',
    // Add more routes as needed
];

// Generate sitemap XML
const sitemapXML = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    ${routes.map(route => `<url><loc>https://peddinti-sriram-bharadwaj.github.io${route}</loc></url>`).join('')}
</urlset>`;

// Write sitemap to file
fs.writeFileSync('./public/sitemap.xml', sitemapXML);
