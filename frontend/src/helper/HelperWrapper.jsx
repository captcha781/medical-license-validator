import React, { Fragment, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { getProfileData } from 'redux/slices/user.slice';

const HelperProfiler = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(getProfileData());
  }, [dispatch]);

  return <Fragment />;
};

export default HelperProfiler;
