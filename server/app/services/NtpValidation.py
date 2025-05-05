from server.app.models.NtpExtraDetails import NtpExtraDetails

class NtpValidation:

    @staticmethod
    def is_valid(details : NtpExtraDetails) -> bool:
        """
        Checks the validity of the details object.
        According to ntp, the 'leap' attribute has only 2 bits and if its value is 3 (11 in binary) 
        then it is invalid.
        
        args:
            details (NtpExtraDetails): The details objects to validate.

        returns:
            bool: True if the provided details have a 'leap' value different from 3,
              False otherwise.
        """
        if details.leap == 3:
            return False
        return True