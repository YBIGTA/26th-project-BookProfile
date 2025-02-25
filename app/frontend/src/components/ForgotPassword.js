import * as React from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';

export default function ForgotPassword({ open, handleClose }) {
  const handleSubmit = (event) => {
    event.preventDefault();
    // 실제 비밀번호 재설정 로직 대신 알림만 표시
    alert('Password reset email would be sent here');
    handleClose();
  };

  return (
    <Dialog open={open} onClose={handleClose}>
      <DialogTitle>Reset Password</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Enter your email address and we'll send you a link to reset your password.
        </DialogContentText>
        <TextField
          autoFocus
          margin="dense"
          id="reset-email"
          label="Email Address"
          type="email"
          fullWidth
          variant="outlined"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleSubmit}>Send Reset Link</Button>
      </DialogActions>
    </Dialog>
  );
}
