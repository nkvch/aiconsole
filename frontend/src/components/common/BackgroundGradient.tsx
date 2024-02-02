const BackgroundGradient = () => {
  return (
    <>
      <div className="absolute w-[1140px] h-[1140px] rounded-full opacity-10 bg-background-gradient top-0 left-0 -translate-y-1/2 -translate-x-1/4 z-0" />
      <div className="absolute w-[1140px] h-[1140px] rounded-full opacity-10 bg-background-gradient top-0 right-0 -translate-y-1/2 translate-x-1/4 z-0" />
    </>
  );
};
export default BackgroundGradient;
