import * as React from 'react';
import SvgIcon from '@mui/material/SvgIcon';

export function GoogleIcon(props) {
  return (
    <SvgIcon {...props}>
      <path d="M21.35 11.1h-9.18v2.88h5.3c-.23 1.24-.95 2.29-2.03 3l3.26 2.53c1.91-1.76 3-4.35 3-7.41 0-.5-.05-.98-.14-1.45z" />
      <path d="M12.17 22c2.75 0 5.07-.91 6.76-2.47l-3.26-2.53c-.9.61-2.06.97-3.5.97-2.69 0-4.96-1.82-5.77-4.27H3.31v2.68A8.003 8.003 0 0 0 12.17 22z" />
      <path d="M6.4 13.73a4.76 4.76 0 0 1 0-3.46V7.59H3.31a8.003 8.003 0 0 0 0 7.83l3.09-1.69z" />
      <path d="M12.17 5.5c1.49 0 2.82.51 3.87 1.52l2.91-2.91C17.22 2.63 14.9 1.5 12.17 1.5a8.003 8.003 0 0 0-7.86 5.09l3.09 2.68c.81-2.45 3.08-4.27 5.77-4.27z" />
    </SvgIcon>
  );
}

export function FacebookIcon(props) {
  return (
    <SvgIcon {...props}>
      <path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.99 3.66 9.12 8.44 9.88v-6.99H7.9v-2.89h2.54V9.41c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.23.2 2.23.2v2.45h-1.26c-1.25 0-1.64.78-1.64 1.58v1.9h2.8l-.45 2.89h-2.35v6.99C18.34 21.12 22 16.99 22 12z" />
    </SvgIcon>
  );
}

export function SitemarkIcon(props) {
  return (
    <SvgIcon {...props}>
      <path d="M12 2L2 7l10 5 10-5-10-5zm0 7l-10-5v10l10 5 10-5V4l-10 5z" />
    </SvgIcon>
  );
}
