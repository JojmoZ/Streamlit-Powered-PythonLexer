num <- 1
while (num <= 100) {
  sisa <- (num %% 2)   
  if (sisa != 0) {
      oddnum <- num
      cat(oddnum, "  ");
      }
   num <- num + 1 
}